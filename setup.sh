#!/bin/bash
man_help(){
    echo "========================================================================"
    echo "Setup of liveorc operational REST API / Admin dashboard on Linux"
    echo "========================================================================"
    echo ''
    echo ''
    echo ''
    echo 'Options:'
    echo '        --all'
    echo '                         Install all dependencies, and software and libraries as is'
    echo ''
    echo '        --dependencies'
    echo '                         Install all dependencies'
    echo ''
    echo '        --liveorc'
    echo '                         Install pyorc environment including all python dependencies (Miniconda required)'
    echo ''
    echo '        --service'
    echo '                         Install pyorc operational service as systemd service with 15-minute timer'
    echo ''
    exit 0
}

install_dependencies () {
    echo '################################'
    echo 'INSTALLING DEPENDENCIES'
    echo '################################'
    if [[ `hostnamectl` =~ .*"CentOS".* ]];
    then
        echo "CentOS system detected, running yum"
	sudo yum -y update
	sudo yum install ffmpeg libsm6 libxext6 libgl1 python3-venv -y
    elif [[ `hostnamectl` =~ .*"Ubuntu".* ]] || [[ `hostnamectl` =~ .*"pop-os".* ]] || [[ `hostnamectl` =~ .*"Mint".* ]];
    then
        echo "Ubuntu-like system detected, trying apt"
        sudo apt -y update
        sudo apt -y upgrade
        sudo apt install ffmpeg libsm6 libxext6 libgl1 python3-venv -y
        sudo apt install -y python3-pip
        sudo apt install -y python3-venv
        sudo apt install -y python3-dev
    else
        echo "System unknown I can't help you with updating"
    fi
}


install_liveorc () {
    echo '################################'
    echo 'INSTALLING LIVEOPENRIVERCAM'
    echo '################################'
        pip3 install virtualenv
        python3 -m venv $HOME/venv/liveorc
        # activate the new environment
        source $HOME/venv/liveorc/bin/activate
        # Setup the python environment
        pip install wheel
        pip install gunicorn
        pip install -r requirements.txt
        # collect static files
        python manage.py collectstatic
        #initiate database tables
        python manage.py migrate
        # make a superuser
        python manage.py createsuperuser
        # deactivate environment
        deactivate

}

install_service () {
    echo '################################'
    echo 'INSTALLING SYSTEMD SERVICE '
    echo '################################'
    echo 'Your .env environmental variables dictate the following settings for the REST API / Admin dashboard setup'
    echo 'Variable                Description                     Value'
    echo '======================= =========================       ===================================='
    echo 'DATABASE_HOST           url to postgresql database      '${DATABASE_HOST}
    echo 'DATABASE_NAME           name of database                '${DATABASE_NAME}
    echo 'DATABASE_USER           username for database           '${DATABASE_USER}
    echo 'DATABASE_PASSWORD       password belonging to username  '${DATABASE_PASSWORD}
    echo 'DATABASE_PORT           port number belonging to host   '${DATABASE_PORT}

    # echo 'DJANGO_SECRET_KEY       Key for hiding Django       '${DJANGO_SECRET_KEY}
    echo 'CELERY_URL              Celery broker connection    '${CELERY_URL}
    echo ''
    read -p 'Are you sure you want to continue with these settings? If you select [n] I will exit. [y/n]' -n 1 -r
    echo    # (optional) move to a new line
    if ! [[ $REPLY =~ ^[Yy]$ ]]
    then
      echo 'Please refine your .env file and return, I will exit now.'
      exit 0
    fi

    echo 'Please enter the domain name of your server'
    read domain_name
    echo
    echo 'Please enter an email address for certificate renewal information'
    read email
    echo
    echo 'installing nginx'
    if ! type "nginx"; then
        sudo apt install -y nginx
    else echo Nginx seems to be already installed
    fi

    # generation of a suitable 32bit 64base encoded fernet key for the DJANGO_SECRET_KEY
    echo "Creating very secure DJANGO_SECRET_KEY from cryptography"
    export passwd=`python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'`
    echo "DJANGO_SECRET_KEY=${passwd}" >> ./.env
    echo "ALLOWED_HOSTS=${domain_name}" >> ./.env
    # uwsgi setup
    echo 'Making a uwsgi gunicorn configuration'
    cat > liveorc.service <<EOF
[Unit]
Description=gunicorn LiveORC daemon
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$PWD
Environment="PATH=${HOME}/venv/liveorc/bin"
Environment="DEBUG=False"
EnvironmentFile=${PWD}/.env
ExecStart=$HOME/venv/liveorc/bin/gunicorn --access-logfile - --workers 3 --bind unix:/tmp/liveorc.sock LiveORC.wsgi:application

[Install]
WantedBy=multi-user.target
EOF


    sudo mv liveorc.service /etc/systemd/system/
    # ensuring credentials are set correctly
    sudo chmod 644 /etc/systemd/system/liveorc.service
    echo 'starting and enabling the 3DStreetview service with Systemd'
    sudo systemctl start liveorc.service
    sudo systemctl enable liveorc.service

    # Nginx setup
    echo 'adding the REST API / Admin dashboard to nginx'
    cat > liveorc.conf <<EOF
server {
    client_max_body_size 512M; # file uploads per request limited to 512M. This should accomodate uploads of large videos
    listen 80;
    server_name $domain_name www.$domain_name;
    location /static/ {
        root $PWD;
    }
    location / {
        include proxy_params;
        proxy_pass http://unix:/tmp/liveorc.sock;
    }
}
EOF
    sudo mv liveorc.conf /etc/nginx/sites-available/
    echo 'creating symlink to LiveORC site in nginx sites-enabled'
    if [ ! -f /etc/nginx/sites-enabled/liveorc.conf ]; then
        sudo ln -s /etc/nginx/sites-available/liveorc.conf /etc/nginx/sites-enabled
    else echo 'Looks like the symlink has already been created'
    fi

    echo 'Installing Certbot...'
    if ! type "certbot"; then
        sudo apt install -y certbot python3-certbot-nginx
    else echo Certbot seems to be already installed
    fi
    echo Procuring a certificate for the site from LetsEncrypt using Certbot
    sudo certbot --nginx -n --agree-tos --redirect -m $email -d $domain_name -d www.$domain_name

    # setup firewall rules
    echo 'Add Nginx HTTP/HTTPS to firewall rules'
    sudo ufw allow 'Nginx HTTP'
    sudo ufw allow 'Nginx HTTPS'


#    echo 'adding the LiveORC service to Systemd'
#    cat > liveorc.service <<EOF
#[Unit]
#Description=uWSGI instance to serve LiveORC
#After=network.target
#
#[Service]
#User=${USER}
#Group=www-data
#WorkingDirectory=${PWD}
#Environment="PATH=${HOME}/venv/liveorc/bin"
#Environment=DEBUG=False
#EnvironmentFile=${PWD}/.env
#ExecStart=${HOME}/venv/liveorc/bin/uwsgi --ini ${PWD}/uwsgi.ini
#Restart=always
#
#[Install]
#WantedBy=multi-user.target
#EOF
}


main() {
    #display parameters
    echo 'Installation options: ' "$@"
    array=("$@")
    # if no parameters display help
    if [ -z "$array" ]                    ; then man_help                        ;fi
    for i in "${array[@]}"
    do
        if [ "$1" == "--help" ]           ; then man_help                        ;fi
        if [ "$i" == "--dependencies" ]   ; then install_dependencies            ;fi
        if [ "$i" == "--liveorc" ]        ; then install_liveorc                 ;fi
        if [ "$i" == "--service" ]        ; then install_service                 ;fi
        if [ "$i" == "--all" ]            ; then install_dependencies            && \
                                                 install_liveorc                 && \
                                                 install_service                 ;fi
    done
}

main "$@"
exit 0
