# LabJackDAQ

A Data Acquisition program primarily using a LabJack. The code also supports the use of Agilent 344XXX series digital multimeters and SmartTool Pro 3600 digital protractors.  

The program includes plotting GUI with a few basic controls and saves all data to csv files for portability.

This program is cross-platform and has been tested on Windows 10 and Linux. The included installation script is for Linux only.

## Installation
1. `cd` into the working directory where you want this folder to live.
2. Either copy the installation script or clone this repository into that folder 
    - For linux, you can use `curl https://raw.githubusercontent.com/jacornelison/LabJackDAQ/master/install_ljd.sh -o install_ljd.sh`
    - the script will clone the repository automatically if the script is either not run in the repo directory or cannot find it in the working directory
3. `sudo bash install_ljd.sh`
4. `source ~/.bashrc`

## Functions

`LabJackDAQ` is currently the sole function in this package. 


## Shortcutting:

After installation, the following alias is added to your `.bashrc`

```
alias ljdaq='sudo python3 ~/path/to/LabJackDAQ/LabJack_DAQ.py'
```

That way, you can start the data acquisition from any directory and it should still work, provided you've done the shortcuts correctly.

## Quick Start

Using the alias above, simply running the program will start the DAQ, saving the data from the `AIN0` channel to `LabJackDAQ/data/labjack_generic_daq.csv`.

The current arguments are:
- `-h, --help`            show this help message and exit
- `-a, --archive`         (Normally off) Puts the DAQ in an archive mode similar
                        to GCP. Meant for long term (i.e. days or weeks) DAQ
                        sessions. All 7 differential analog inputs from the LJ
                        will be readout with generic input names (e.g. AIN0,
                        AIN2, etc...) and new archive files will be created
                        when file sizes reach a certain size to reduce
                        computational load (Currently arbitrarily set to 200MB
                        which lasts ~20hrs at 50ms sample rate). Forces
                        options: `-dm --ch AIN0,AIN2,AIN4,...,AIN12
                        --title yymmdd_HHMMSS`
-  `--ch CH`               Select number of channels up to 13 by naming them.
                        E.g. "T,V,T2,V2" (for labjack only)
-  `-d, --diff`            Take Differential readings. Pos input on even
                        channels, negative on input channel+1 (Normally off)
-  `--dir DIR`             dir in filename
-  `--dmm`                 Utilize Agilent DMM instead of U6 for DAQ, only 1
                        channel. (Normally off)
-  `-i, --inc`             Toggle acquisition from digital inclinometer (normally
                        off)
-  `-m, --mjd`             Timestamps will be converted to MJD (Normally off)
-  `-o, --ow`              Overwrite input file. (Normally off)
-  `--refreshrate REFRESHRATE`
                        Set plot refresh rate in milliseconds Default = 50
-  `--samprate SAMPRATE`   Set sample rate in milliseconds
-  `-t, --test`            Disables DAQs and writes fake data for testing.
                        (Normally off)
-  `--title TITLE`         Change the default filename. def =
                        labjack_generic_daq.csv


##### Examples

- Read from 3 channels using a LabJack
    - `ljdaq --ch "Temp,V1,V2"`
- Save to a custom directory using a custom name
    - `ljdaq --dir "path/to/data/" --title "data_name.csv"`
- Read from an Agilent dmm and a digital protractor
    - `ljdaq --dmm --inc`
- Read two differential measurements between `AIN0`/`AIN1` and `AIN2`/`AIN3` (high/low respectively)
    - `ljdaq --diff --ch "Resistor 1,Resistor 2"`
- Read a single differential measurement, include the inclinometer and overwrite any files
    - `ljdaq -d -i -o` or `ljdaq -dio`    

## Notes
- The data folder is for local use only. There's a `gitignore` that excludes `.csv` files to prevent large data files from being committed.
- Differential readings can not be toggled for specific channels. Either all channels are differential or none are. Plan accordingly.
- The GUI is created by `pyqtgraph`. If you want to add any updates to the GUI, a great repository of knowledge is in the examples program.
    - `>>> import pyqtgraph.examples`
    - `>>> pyqtgraph.examples.run()` 
