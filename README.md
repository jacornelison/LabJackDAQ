# LabJackDAQ

A Data Acquisition program primarily using a LabJack. The code also supports the use of Agilent 344XXX series digital multimeters and SmartTool Pro 3600 digital protractors.  

The program includes plotting GUI with a few basic controls and saves all data to csv files for portability.

This program is cross-platform and has been tested on Windows 10 and Linux. The included installation script is for Linux only.

## Installation
1. `cd` into the working directory where you want this folder to live.
2. Either copy the installation script or clone this repository into that folder 
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

Some important arguments are:
- `--title` - Sets the name of the data for saving. If the name already exists and overwrite is not enabled (`--ow`), the title have a sequential number appended to it (`your_title_1.csv`, `your_title_2.csv`, etc...). 
- `--dir` - Sets the 'data' directory in which files output from the DAQ is saved.
- `--ch` - Sets the names of the channels to be read. Each channel is read referenced to ground.
- `--dmm` - Instead of using the LabJack, will instead try to read a single channel from an Agilent DMM
- `--inc` - In addition to reading voltage data, an extra channel will be added which reads out of a Pro 3600 digital protractor.  
- `--diff` - Reads a differential measurement between two `AIN` channels. Even channel numbers are the high side, the subsequent channel reads the low side.
There's a few options that can be passed in the arguments.
Check the help for more info (i.e. `python LabJack_DAQ.py --help`)

##### Examples

- Read from 3 channels using a LabJack
    - `ljdaq --ch "Temp,V1,V2"`
- Save to a custom directory using a custom name
    - `ljdaq --dir "path/to/data/" --title "data_name.csv"`
- Read from an Agilent dmm and a digital protractor
    - `ljdaq --dmm --inc`
- Read two differential measurements between `AIN0`/`AIN1` and `AIN2`/`AIN3` (high/low respectively)
    - `ljdaq --diff --ch "Resistor 1,Resistor 2"`
    

## Notes
- The data folder is for local use only. There's a `gitignore` that excludes `.csv` files to prevent large data files from being committed.
- Differential readings can not be toggled for specific channels. Either all channels are differential or none are. Plan accordingly.
- The GUI is created by `pyqtgraph`. If you want to add any updates to the GUI, a great repository of knowledge is in the examples program.
    - `>>> import pyqtgraph.examples`
    - `>>> pyqtgraph.examples.run()` 
