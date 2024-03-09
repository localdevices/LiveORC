#!/bin/bash
set -eo pipefail
__dirname=$(cd "$(dirname "$0")"; pwd -P)
cd "${__dirname}"

platform="Linux" # Assumed
uname=$(uname)
case $uname in
        "Darwin")
        platform="MacOS / OSX"
        ;;
        MINGW*)
        platform="Windows"
        ;;
esac

if [[ $platform = "Windows" ]]; then
        export COMPOSE_CONVERT_WINDOWS_PATHS=1
fi

dev_mode=false
gpu=false

# define realpath replacement function
if [[ $platform = "MacOS / OSX" ]]; then
    realpath() {
        [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
    }
fi

# Load default values
source "${__dirname}/.env"
DEFAULT_PORT="$LORC_PORT"
DEFAULT_HOST="$LORC_HOST"
DEFAULT_MEDIA_DIR="$LORC_MEDIA_DIR"
DEFAULT_DB_DIR="$LORC_DB_DIR"
DEFAULT_SSL="$LORC_SSL"
DEFAULT_SSL_INSECURE_PORT_REDIRECT="$LORC_SSL_INSECURE_PORT_REDIRECT"

# Parse args for overrides
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --port)
    export LORC_PORT="$2"
    shift # past argument
    shift # past value
    ;;
    --hostname)
    export LORC_HOST="$2"
    shift # past argument
    shift # past value
    ;;
    --media-dir)
    LORC_MEDIA_DIR=$(realpath "$2")
    export LORC_MEDIA_DIR
    shift # past argument
    shift # past value
    ;;
    --db-dir)
    LORC_DB_DIR=$(realpath "$2")
    export LORC_DB_DIR
    shift # past argument
    shift # past value
    ;;
    --ssl)
    export LORC_SSL=YES
    shift # past argument
    ;;
    --ssl-key)
    LORC_SSL_KEY=$(realpath "$2")
    export LORC_SSL_KEY
    shift # past argument
    shift # past value
    ;;
    --ssl-cert)
    LORC_SSL_CERT=$(realpath "$2")
    export LORC_SSL_CERT
    shift # past argument
    shift # past value
    ;;
    --ssl-insecure-port-redirect)
    export LORC_SSL_INSECURE_PORT_REDIRECT="$2"
    shift # past argument
    shift # past value
    ;;
#    --debug)
#    export LORC_DEBUG=YES
#    shift # past argument
#    ;;
#    --dev)
#    export LORC_DEBUG=YES
#    export LORC_DEV=YES
#    dev_mode=true
#    shift # past argument
#    ;;
#    --broker)
#    export LORC_BROKER="$2"
#    shift # past argument
#    shift # past value
#    ;;
#    --no-default-node)
#    echo "ATTENTION: --no-default-node is deprecated. Use --default-nodes instead."
#    export WO_DEFAULT_NODES=0
#    shift # past argument
#    ;;
    --detached)
    detached=true
    shift # past argument
    ;;
#    --settings)
#    LORC_SETTINGS=$(realpath "$2")
#    export WO_SETTINGS
#    shift # past argument
#    shift # past value
#    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameter

usage(){
  echo "Usage: $0 <command>"
  echo
  echo "This program helps to manage the setup/teardown of the docker containers for running LiveORC."
  echo "This script was adopted and modified from https://github.com/OpenDroneMap/WebODM/"
  echo "We recommend that you read the full documentation of docker at https://docs.docker.com if you want to customize your setup."
  echo
  echo "Command list:"
  echo "        start [options]         Start LiveORC"
  echo "        stop                    Stop LiveORC"
  echo "        down                    Stop and remove LiveORC's docker containers"
#  echo "        update                  Update LiveORC to the latest release"
#  echo "        liveupdate              Update LiveORC to the latest release without stopping it"
  echo "        rebuild                 Rebuild all docker containers and perform cleanups"
#  echo "        checkenv                Do an environment check and install missing components"
#  echo "        test                    Run the unit test suite (developers only)"
#  echo "        resetadminpassword \"<new password>\"   Reset the administrator's password to a new one. LiveORC must be running when executing this command and the password must be enclosed in double quotes."
  echo ""
  echo "Options:"
  echo "        --port  <port>  Set the port that LiveORC should bind to (default: $DEFAULT_PORT)"
  echo "        --hostname      <hostname>      Set the hostname that LiveORC will be accessible from (default: $DEFAULT_HOST)"
#  echo "        --media-dir     <path>  Path where processing results will be stored to (default: $DEFAULT_MEDIA_DIR (docker named volume))"
#  echo "        --db-dir        <path>  Path where the Postgres db data will be stored to (default: $DEFAULT_DB_DIR (docker named volume))"
#  echo "        --default-nodes The amount of default NodeODM nodes attached to LiveORC on startup (default: $DEFAULT_NODES)"
#  echo "        --with-micmac   Create a NodeMICMAC node attached to LiveORC on startup. Experimental! (default: disabled)"
  echo "        --ssl   Enable SSL and automatically request and install a certificate from letsencrypt.org. (default: $DEFAULT_SSL)"
  echo "        --ssl-key       <path>  Manually specify a path to the private key file (.pem) to use with nginx to enable SSL (default: None)"
  echo "        --ssl-cert      <path>  Manually specify a path to the certificate file (.pem) to use with nginx to enable SSL (default: None)"
  echo "        --ssl-insecure-port-redirect    <port>  Insecure port number to redirect from when SSL is enabled (default: $DEFAULT_SSL_INSECURE_PORT_REDIRECT)"
  echo "        --debug Enable debug for development environments (default: disabled)"
#  echo "        --dev   Enable development mode. In development mode you can make modifications to LiveORC source files and changes will be reflected live. (default: disabled)"
#  echo "        --dev-watch-plugins     Automatically build plugins while in dev mode. (default: disabled)"
#  echo "        --broker        Set the URL used to connect to the celery broker (default: $DEFAULT_BROKER)"
  echo "        --detached      Run LiveORC in detached mode. This means LiveORC will run in the background, without blocking the terminal (default: disabled)"
#  echo "        --gpu   Use GPU NodeODM nodes (Linux only) (default: disabled)"
#  echo "        --settings      Path to a settings.py file to enable modifications of system settings (default: None)"
#  echo "        --worker-memory Maximum amount of memory allocated for the worker process (default: unlimited)"
#  echo "        --worker-cpus   Maximum number of CPUs allocated for the worker process (default: all)"

  exit
}

get_secret(){
    # re-used from https://github.com/OpenDroneMap/LiveORC/
    if [ ! -e ./.secret_key ] && [ -e /dev/random ]; then
        echo "Generating secret in ./.secret_key"
        export WO_SECRET_KEY=$(head -c50 < /dev/random | base64)
        echo $LORC_SECRET_KEY > ./.secret_key
    elif [ -e ./.secret_key ]; then
        export WO_SECRET_KEY=$(cat ./.secret_key)
    else
        export WO_SECRET_KEY=""
    fi
}

run(){
        echo "$1"
        eval "$1"
}

start(){
	# use assembled options to start the LiveORC environment
	# retrieve a secret key
	get_secret


	echo "Starting LiveORC..."
	echo ""
	echo "Using the following environment:"
	echo "================================"
	echo "Host: $LORC_HOST"
	echo "Port: $LORC_PORT"
#	echo "Media directory: $LORC_MEDIA_DIR"
#	echo "Postgres DB directory: $LORC_DB_DIR"
	echo "SSL: $LORC_SSL"
	echo "SSL key: $LORC_SSL_KEY"
	echo "SSL certificate: $LORC_SSL_CERT"
	echo "SSL insecure port redirect: $LORC_SSL_INSECURE_PORT_REDIRECT"
	echo "================================"
	echo "Make sure to issue a $0 down if you decide to change the environment."
	echo ""

	# assemble a command, extended with options further onwards
	command="docker compose -f docker-compose.yml"

	if [ "$LORC_SSL" = "YES" ]; then
		enable_ssl
	fi
    command="$command up"

	if [[ $detached = true ]]; then
			command+=" -d"
	fi
	run "${command}"
}
down(){
	command="docker compose -f docker-compose.yml"
	run "${command}"
}

stop(){
	echo "Stopping LiveODM..."

	command="docker compose -f docker-compose.yml"
	command+=" stop"
	run "${command}"

}
rebuild(){
	run "docker compose down --remove-orphans"
	run "docker compose -f docker-compose.yml build --no-cache"
	echo -e "\033[1mDone!\033[0m You can now start LiveODM by running $0 start"
}

enable_ssl(){
	if [ -n "$LORC_SSL_KEY" ] && [ ! -e "$LORC_SSL_KEY" ]; then
			echo -e "\033[91mSSL key file does not exist: $LORC_SSL_KEY\033[39m"
			exit 1
	fi
	if [ -n "$LORC_SSL_CERT" ] && [ ! -e "$LORC_SSL_CERT" ]; then
			echo -e "\033[91mSSL certificate file does not exist: $LORC_SSL_CERT\033[39m"
			exit 1
	fi
	command+=" -f docker-compose.ssl.yml"

	method="Lets Encrypt"
	if [ -n "$LORC_SSL_KEY" ] && [ -n "$LORC_SSL_CERT" ]; then
			method="Manual"
			command+=" -f docker-compose.ssl-manual.yml"
	fi

	if [ "$method" = "Lets Encrypt" ]; then
			# Check port settings
			# as let's encrypt cannot communicate on ports
			# different than 80 or 443
			if [ "$LORC_PORT" != "$DEFAULT_PORT" ]; then
					echo -e "\033[93mLets Encrypt cannot run on port: $LORC_PORT, switching to 443.\033[39m"
					echo "If you need to use a different port, you'll need to generate the SSL certificate files separately and use the --ssl-key and --ssl-certificate options."
			fi
			export WO_PORT=443
	fi

	# Make sure we have a hostname
	if [ "$LORC_HOST" = "localhost" ]; then
			echo -e "\033[91mSSL is enabled, but hostname cannot be set to $LORC_HOST. Set the --hostname argument to the domain of your LiveORC server (for example: www.myLiveORC.org).\033[39m"
			exit 1
	fi

	echo "Will enable SSL ($method)"

}

if [[ $1 = "start" ]]; then
	start
elif [[ $1 = "stop" ]]; then
	stop
elif [[ $1 = "restart" ]]; then
	down
	start
elif [[ $1 = "down" ]]; then
	down
elif [[ $1 = "rebuild" ]]; then
	echo "Rebuilding LiveORC..."
	rebuild
#elif [[ $1 = "update" ]]; then
#	down
#	update
#	echo -e "\033[1mDone!\033[0m You can now start LiveORC by running $0 start"
else
	usage
fi