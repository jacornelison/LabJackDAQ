#! /bin/bash

go ()
{
	$@
	ret=$?
	if [ $ret -ne 0 ]; then
		echo "Error, please make sure you are running this script as:"
		echo "  $ sudo $0"
		exit $ret
	fi
}

if [ "$OSTYPE" -ne "linux-gnu" ]; then
    echo "Operating System: $OSTYPE detected."
    echo "This installation only works on Linux machines right now."
fi

# Get python and pip
printf "\n\n\nInstalling Python3/pip...\n\n\n"
go apt-get -y install python3
go apt-get -y install python3-pip

# Ensure we have build-ess., libusb, and git for exodriver
printf "\n\n\nChecking for required packages...\n\n\n"
go apt-get -y install build-essential
go apt-get -y install libusb-1.0-0-dev
go apt-get -y install git-core

# Get and install exodriver
printf "\n\n\nInstalling Exodriver...\n\n\n"
go git clone git://github.com/labjack/exodriver.git
go cd exodriver/
go ./install.sh
go cd ..

# Get labjackpython
printf "\n\n\nInstalling labjackpython...\n\n\n"
go git clone git://github.com/labjack/LabJackPython.git
go cd LabJackPython/
go python3 -m pip install --user .
go cd ..

# Now setup LabJackDAQ
printf "\n\n\nSetting up LabJackDAQ...\n\n\n"
go git clone git://github.com/jacornelison/LabJackDAQ.git
go cd LabJackDAQ
go python3 -m pip install --user .

# Make aliases for python
LJ_ALIAS="alias ljdaq='python3 $PWD/LabJackDAQ.py"

if ! grep -q "$LJ_ALIAS" ~/.bashrc; then
  echo $LJ_ALIAS >> ~/.bashrc
  source ~/.bashrc
fi

