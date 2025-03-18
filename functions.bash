

#
# useful functions
#

vecho() {
   if [ "$VERBOSE" -ne "0" ]; then
      echo "$1: $2"
   fi
}

valid_ipv4() {
    local ip="$1"
    err_msg='IP address is invalid'
    [[ "$ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] || { echo "$0: $err_msg 1"; return 1; }
    for i in ${ip//./ }; do
        [[ "${#i}" -gt 1 && "${i:0:1}" == 0 ]] && { echo "$0: $err_msg 2"; return 1; }
        [[ "$i" -gt 255 ]] && { echo "$0: $err_msg 3"; return 1; }
    done
    return 0
}

silent_background() {
    echo "$0: CMD: $@"
    { PYTHONPATH=ipmicap 2>&3 "$@"& } 3>&2 2>-
    disown &>/dev/null  # Close STD{OUT,ERR} for silence if job has already completed
}

check_python_env() {
    vecho $0 "Checking python environment for $1"
    python -c "import $1" >/dev/null 2>&1
    if [ "$?" -ne "0" ]; then
        echo "$0: ERROR: Missing critical python package(s).  Are you sure you have activated the right python environment?"
        exit 1
    fi
}

check_results_dir() {
    vecho $0 "Checking $1 dir not already exists..."
    if [ -d "$1" ]; then
        echo "$0: The $1 dir already exists. Please delete or move it. Content of $1 dir = "
        ls -als $1
        exit 1
    fi
}

check_ipmicap_port() {
    vecho $0 "Checking nothing is running at port at $1..."
    lsof -i ":$1"
    if [ "$?" -eq "0" ]; then
        echo "$0: ERROR: There is something already listing on the port at $1.  Kill that process or choose a different port."
        exit 1
    fi
}

reset_docker() {
    # make sure docker is installed
    echo "$0: Resetting docker environment. Please wait..."
    docker version >/dev/null 2>&1
    if [ "$?" -ne "0" ]; then
        echo "$0: Docker is not valid"
        exit 1
    fi

    # get current containers
    CUR_DOCKER=$(docker ps -a -q 2>&1)
    if [ "$?" -ne "0" ]; then
        echo "$0: Could enumerate currently running docker containers."
        exit 1
    fi

    # stop/rm docker containers as needed
    if [ -z "$CUR_DOCKER" ]; then
       vecho $0 "No docker containers were running..."
    else
        vecho $0 "Stopping/removing all docker containers..."
        docker ps -aq | xargs docker rm -f >/dev/null 2>&1
        if [ "$?" -ne "0" ]; then
            echo "$0: Could not stop and remove all docker containers."
            exit 1
        fi
    fi

    vecho $0 "Restarting docker..."
    sudo service docker restart
}

reset_ipmi() {
    echo "$0: Resetting ipmi environment.  Please wait..."

    # determine ipmitool is installed
    vecho $0 "Checking ipmitool is installed..."
    which ipmitool >/dev/null 2>&1
    if [ "$?" -ne "0" ]; then
        echo "$0: ERROR: Could not find ipmitool.  Is it installed?"
        exit 1
    fi

    # load the ipmi user and password
    if [ -f ./.ipmi_secrets ]; then
        vecho $0 "Found ipmi_secrets file..."
        source ./.ipmi_secrets
    else
        echo "$0: ERROR: Expecting to find './.ipmi_secrets' file"
        exit 1
    fi
    if [ -z "$IPMI_USER" ]; then
        echo "$0: ERROR: IPMI_USER env var not found."
        exit 1
    fi
    if [ -z "$IPMI_PASS" ]; then
        echo "$0: ERROR: IPMI_PASS env var not found."
        exit 1
    fi
    if [ -z "$IPMI_RECORDS" ]; then
        echo "$0: ERROR: IPMI_RECORDS env var not found."
        exit 1
    fi

    # get the IPMI ip of the machine
    if [ -z "$3" ]; then
        # run ipmitool to get the IPMI IP address
        vecho $0  "Getting IPMI ip address..."
        IPMI_IP=`sudo ipmitool lan print | awk '$1=="IP" && $2=="Address" && $3==":" {print $4}'`
        if [ -z "$IPMI_IP" ]; then
            echo "$0: ERROR: Could not get IPMI ip address.  Are you sure it's setup?"
            exit 1
        fi
    else 
        # run ipmitool to get the IPMI IP address
        vecho $0  "Getting IPMI ip address..."
        IPMI_IP=`sudo ipmitool -H "$IPMI_IP" -U "$IPMI_USER" -P "$IPMI_PASS" lan print | awk '$1=="IP" && $2=="Address" && $3==":" {print $4}'`
        if [ -z "$IPMI_IP" ]; then
            echo "$0: ERROR: Could not get IPMI ip address.  Are you sure it's setup?"
            exit 1
        fi
    fi

    # validate correct address format
    valid_ipv4 "$IPMI_IP"
    if [ "$?" -ne "0" ]; then
        echo "$0: ERROR: Invalid IP address format ->$IPMI_IP<-"
        exit 1
    fi
    vecho $0 "Found IPMI ip address=$IPMI_IP"

    # reset IPMI
    echo "$0: Resetting ipmi interface at $IPMI_IP..."
    ipmitool -H "$IPMI_IP" -U "$IPMI_USER" -P "$IPMI_PASS" mc reset cold >/dev/null 2>&1
    if [ "$?" -ne "0" ]; then
        echo "$0: ERROR: Could not reset ipmi interface at $IPMI_IP"
        exit 1
    fi
    sleep 4 # TODO: need a way to determine if it received the command

    # run ipmi sanity check in loop until it appears to be up again
    while : ; do
        echo "$0: Waiting for IPMI at $IPMI_IP..."
        sleep 2
        ipmitool -H "$IPMI_IP" -U "$IPMI_USER" -P "$IPMI_PASS" sensor 2>&1 | grep "$1" | grep "$2" >/dev/null 2>&1
        if [ "$?" -eq "0" ]; then
            echo "$0: IPMI is back up."
            break
        fi
    done
}

reset_ipmicap() {

    # check that nothing is listening on that the ipmicap port
    vecho $0 "Checking nothing is running at port at $1..."
    lsof -i ":$1"
    if [ "$?" -eq "0" ]; then
        echo "$0: ERROR: There is something already listing on the port at $1.  Kill that process or choose a different port."
        exit 1
    fi

    # form ipmicap --debug flag as needed
    IPMI_FLAGS=""
    if [ "$IPMICAP_VERBOSE" -ne "0" ]; then
        IPMI_FLAGS="--debug"
    fi

    # load the ipmi user and password and records
    if [ -f ./.ipmi_secrets ]; then
        vecho $0 "Found ipmi_secrets file..."
        source ./.ipmi_secrets
    else
        echo "$0: ERROR: Expecting to find './.ipmi_secrets' file"
        exit 1
    fi
    if [ -z "$IPMI_USER" ]; then
        echo "$0: ERROR: IPMI_USER env var not found."
        exit 1
    fi
    if [ -z "$IPMI_PASS" ]; then
        echo "$0: ERROR: IPMI_PASS env var not found."
        exit 1
    fi
    if [ -z "$IPMI_RECORDS" ]; then
        echo "$0: ERROR: IPMI_RECORDS env var not found."
        exit 1
    fi

    # run ipmitool to get the IPMI IP address
    vecho $0  "Getting IPMI ip address..."
    IPMI_IP=`sudo ipmitool lan print | awk '$1=="IP" && $2=="Address" && $3==":" {print $4}'`
    if [ -z "$IPMI_IP" ]; then
        echo "$0: ERROR: Could not get IPMI ip address.  Are you sure it's setup?"
        exit 1
    fi

    # launch ipmicap server (5029)
    echo "$0: Launching ipmicap server at port at $1..."
    PYTHONPATH="ipmicap" python -u ipmicap/ipmicap.py --ip "$IPMI_IP" --iface "lan" \
        --delay $IPMI_SAMPLE_DELAY $IPMI_FLAGS \
        --username "$IPMI_USER" \
        --password "$IPMI_PASS" \
        --listen "$1" \
        --sessions  \
        --nologger \
        --records $IPMI_RECORDS &
    if [ "$?" -ne "0" ]; then
        echo "$0: ERROR: Could not launch the ipmicap server."
        exit 1
    fi
    IPMICAP_PID="$!"
    vecho $0 "Found ipmicap server with pid=$IPMICAP_PID..."

    # make sure the ipmicap server launched ok
    vecho $0 "Checking ipmicap server launched ok..."
    sleep 2
    pgrep -af "ipmicap.py"
    if [ "$?" -ne "0" ]; then
        echo "$0: ERROR: Could not verify that ipmicap server launched at port=$IPMICAP_PORT."
        exit 1
    fi

    echo "$IPMICAP_PID"
}

kill_ipmicap() {
    if [ -z "$1" ]; then
        vecho $0 "WARNING: No ipmicap server to stop."
    else
        vecho $0 "WARNING: Stopping ipmicap server with PID=$1"
        kill "$1"
    fi
}

set_sar_config_boards() {
    CONTENT='{"logging_level": "DEBUG", "redis_host": "IPADDR", "redis_port": "6380", "num_of_boards": BRD, "ftp_folder": "", "allocation_id": "default"}'
    IPADDR=$(ip -o route get to 8.8.8.8 | sed -n 's/.*src \([0-9.]\+\).*/\1/p')
    REPLACED=$(python -c "print('$CONTENT'.replace(\"BRD\",\"$1\").replace(\"IPADDR\",\"$IPADDR\"))")
    echo $REPLACED > "/home/public/sar/sar-server/config/config.properties"
    chmod ugo+r "/home/public/sar/sar-server/config/config.properties"
}

#
# function to reset docker and the sar containers
#
reset_sar_docker() {
    if [ "$BYPASS_RESTART_DOCKER" -ne "0" ]; then
        echo "$0: Bypassing resetting of the docker environment..."
    else
        vecho $0 "Resetting docker..."
        reset_docker

        vecho $0 "Setting SAR config for $1 boards"
        set_sar_config_boards $1

        vecho $0 "Restarting docker sar containers..."
        CUR_DIR=$(pwd)
        cd async-sar-api/devops/run_docker && ./prod-run.sh >/dev/null 2>&1
        if [ "$?" -ne "0" ]; then
            echo "$0: Could not restart sar containers."
            exit 1
        fi
        cd "$CUR_DIR"
    fi
}

