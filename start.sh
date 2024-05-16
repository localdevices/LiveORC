#!/bin/bash
echo "Running migrations"
# Set host and port number (with defaults if not available)
export LORC_HOST="${LORC_HOST:=localhost}"
export LORC_PORT="${LORC_PORT:=8000}"

# Dump environment to .cronenv
printenv > .cronenv


congrats(){
    (sleep 10; echo

    echo "Trying to establish communication..."
    status=$(curl --max-time 300 -L -s -o /dev/null -w "%{http_code}" "$proto://localhost:8000")

    if [[ "$status" = "200" ]]; then
        echo -e "\033[92m"
        echo "Congratulations! 🤩 "
        echo "==================="
        echo -e "\033[39m"
        echo "If there are no errors, LiveORC should be up and running!"
    else
        echo -e "\033[93m"
        echo "Something doesn't look right! 🥺 "
        echo "The server returned a status code of $status when we tried to reach it."
        echo "======================================================================="
        echo -e "\033[39m"
        echo "Check if LiveORC is running, maybe we tried to reach it too soon."
    fi

    echo -e "\033[93m"
    echo "Open a web browser and navigate to $proto://$LORC_HOST:$LORC_PORT 🌎 "
    echo -e "\033[39m") &
}

proto="http"
if [ "$LORC_SSL" = "YES" ]; then
    proto="https"
fi

python manage.py migrate
if [ "$1" = "--no-gunicorn" ]; then
    echo "Running LiveORC locally"
    congrats
    python manage.py runserver 0.0.0.0:8000
else
    echo "Running LiveORC with gunicorn"
    if [ -e /liveorc ] && [ ! -e /liveorc/static ]; then
       echo -e "\033[91mWARN:\033[39m /liveorc/static does not exist, CSS, JS and other files might not be available."
    fi
    # replace env variables for hard coded variables
    echo "Generating nginx configurations from templates..."
    for templ in nginx/*.template
    do
        echo "- ${templ%.*}"
        envsubst '\$LORC_PORT \$LORC_HOST' < $templ > ${templ%.*}
    done

    # Check if we need to auto-generate SSL certs via letsencrypt
    if [ "$LORC_SSL" = "YES" ] && [ -z "$LORC_SSL_KEY" ]; then
        echo "Launching letsencrypt-autogen.sh"
        ./nginx/letsencrypt-autogen.sh
    fi


    # Check if SSL key/certs are available
    conf="nginx.conf"
    if [ -e nginx/ssl ]; then
        echo "Using nginx SSL configuration"
        conf="nginx-ssl.conf"
    fi

    # first start nginx
    congrats
    nginx -c $(pwd)/nginx/$conf
    gunicorn --access-logfile - --bind unix:/tmp/liveorc.sock LiveORC.wsgi:application --workers $((2*$(grep -c '^processor' /proc/cpuinfo)+1)) --preload

fi

