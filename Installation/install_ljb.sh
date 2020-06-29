#! /bin/bash

go ()
{
	$@
	ret=$?
	if [ $ret -ne 0 ]; then
		echo "Error, please make sure you are running this script as:"
		echo "  $ sudo $0"
		echo "If you are still having problems, please contact LabJack support: <$SUPPORT_EMAIL>"
		exit $ret
	fi
}

if [ "$OSTYPE" -ne "linux-gnu" ]; then
    echo "Operating System: $OSTYPE detected."
    echo "This installation only works on Linux machines right now."
fi

# Get python and pip
go apt-get install python3
go apt-get install python3-pip

# Ensure we have build-ess., libusb, and git for exodriver
go apt-get install build-essential
go apt-get install libusb-1.0-0-dev
go apt-get install git-core

# Get and install exodriver
go git clone git://github.com/labjack/exodriver.git
go cd exodriver/
go ./install.sh
go cd ..

# Get labjackpython
go git clone git://github.com/labjack/LabJackPython.git
go cd LabJackPython/
go python3 setup.py install

# Now setup LabJackDAQ
go cd ../..
go python3 setup.py install