#!/bin/bash
ABSPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $ABSPATH/autoinstall_config
source $ABSPATH/autoinstall_functions

cd $ABSPATH

rm -f $LOGFILE

# Show help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    showhelp
    exit 0;
fi

# Upload the script and all related files to remote
if [ "$#" -eq 2 ] && [ "$1" = "--upload" ]; then
    statusmsg "Uploading Scripts to host $2 " "PREP"
    RET=$(upload $2 pi raspberry ./\*)
    statusmsg "Uploading Scripts to host $2 " "$RET"
    exit 0;
fi

# Upload the files and install them
if [ "$#" -eq 3 ] && [ "$1" = "--upload" ] && [ "$2" = "--install" ]; then
    statusmsg "Uploading Scripts to host $3 " "PREP"
    RET=$(upload raspberrypi pi raspberry "[!.]*")
    statusmsg "Uploading Scripts to host $3 " "$RET"

    if [ "$RET" != "DONE" ]; then exit 1; else RET="";fi;

    statusmsg "Enable Root with password $ROOTPWD" "PREP"
    RET=$(enableroot $ROOTPWD $3)
    statusmsg "Enable Root with password $ROOTPWD" "$RET"

    if [ "$RET" != "DONE" ]; then exit 1; else RET="";fi;

    if [ -s $SSHFILE ];then
        statusmsg "Copy ssh keys from $SSHFILE to authorized_hosts" "PREP"
        RET=$(copysshid root $ROOTPWD $3 $SSHFILE)
        statusmsg "Copy ssh keys from $SSHFILE to authorized_hosts" "$RET"
    fi

    statusmsg "Run remote autoinstall" "PREP"
    RET=$(autoinstall $3 $ROOTPWD)
    statusmsg "Run remote autoinstall" "$RET"
    exit 0;
fi

# Login to remote device
if [ "$#" -ge 2 ] && [ "$1" = "--login" ]; then
    login $2 pi raspberry
    exit 0;
fi

# Copy SSH keys from file to authorized hosts
if [ "$#" -ge 2 ] && [ "$1" = "--copyid" ]; then

    statusmsg "Copy ssh keys from $SSHFILE to authorized_hosts" "PREP"
    RET=$(copysshid root $ROOTPWD $2 $SSHFILE)
    statusmsg "Copy ssh keys from $SSHFILE to authorized_hosts" "$RET"
    exit 0;
fi


# Enable root to local pi device
if [ "$#" -eq 1 ] && [ "$1" = "--enableroot" ]; then
    statusmsg "Enable Root with password $ROOTPWD" "PREP"
    RET=$(enableroot $ROOTPWD)
    statusmsg "Enable Root with password $ROOTPWD" "$RET"
    echo -e "Please reboot and log-in as root with password $ROOTPWD"
    exit 0;
fi

# Enable root to remote pi device
if [ "$#" -eq 2 ] && [ "$1" = "--enableroot" ]; then
    statusmsg "Enable Root with password $ROOTPWD" "PREP"
    RET=$(enableroot $ROOTPWD $2)
    statusmsg "Enable Root with password $ROOTPWD" "$RET"
    exit 0;
fi

# Main install (meant to be run remotely on device)
if [ "$#" -eq 1 ] && [ "$1" = "--install" ]; then
    # Simplistic detection of PI device
    if  [[ -z $(cat /proc/cpuinfo|grep Serial) ]]; then
        echo "Does not appear to be a raspberrypi device"
        exit 0;
    fi

    # Add password to user root
    if [ "$USER" != "root" ]; then
        echo -e "Please log again as root run the script again."
    exit 0
    fi

    # Delete user pi if it exists
    if  [ $(cat /etc/passwd | grep pi) ]; then
        statusmsg "Removing pi user" "PREP"
        sudo deluser -remove-home pi
        statusmsg "Removing pi user" "DONE"

    fi

    # Configure default shell to bash
    #echo -e "dash   dash/sh boolean false" | debconf-set-selections
    #DEBIAN_FRONTEND=noninteractive dpkg-reconfigure dash

    # Install packages using apt-get install
    statusmsg "Installing debian packages from $APTFILE" "PREP"
    echo -e ""
    multiinstall $APTFILE
    statusmsg "Installing debian packages from $APTFILE" "$(ret2print $?)"

    # Install local prepackaged files
    statusmsg "Installing local debian packages from $DEBDIR" "PREP"
    echo -e ""
    debinstall $DEBDIR
    statusmsg "Installing debian packages from $DEBDIR" "$(ret2print $?)"

    # Install packages using pip
    statusmsg "Installing pip packages from $PIPFILE" "PREP"
    echo -e ""
    pipinstall $PIPFILE
    statusmsg "Installing pip packages from $PIPFILE" "$(ret2print $?)"

    # Checkout code in git
    statusmsg "Checking out code from $GITFILE" "PREP"
    echo -e ""
    CDIR=$(pwd)
    mkdir -p $GITDIR && cd $GITDIR
    RET=$(gitcheckout $GITFILE)
    cd $CDIR
    statusmsg "Checking out code from $GITFILE" "$RET"

    statusmsg "Autoinstall Completed" "DONE"
    exit 0;
fi

showhelp
