# LabJackDAQ


## Functions

This includes two primary functions, `LabJack_DAQ.py` and `plt_data.py`

`LabJack_DAQ` is capable of reading from multiple analog inputs at the AIN inputs either at the terminals of the U6Pro or via the DB25. With no inputs, the code will simply start collecting data from AIN0 at a rate of 1Hz.

`plt_data` is to be used for plotting the data as soon as it is acquired. With no further inputs, the plotter will default to plotting data from the most recently modified csv file in the `LabJackDAQ/data/` folder.

Check the help for more info (i.e. `python LabJack_DAQ.py --help`)

## Shortcutting:

After installation, add these aliases to your `.bashrc`:

```
alias ljdaq='python ~/LabJackDAQ/LabJack_DAQ.py'
alias dataplot='python ~/LabJackDAQ/plt_data.py'
```

That way, you can start the data acquisition from any directory and it should still work, provided you've done the shortcuts correctly.

## Quick Start

Provided you've done the above, open two terminals. In the first terminal, start the data acquisition using `ljdaq` and then enter `auto`.

In the other window, simply enter `dataplot` and the plotter should start plotting the data you've acquired so far. Hit enter in the plotter's terminal to update the values or any positive number to plot the last N samples acquired.


## Notes
- The data folder is for local use only. There's a `gitignore` that excludes `.csv` files to prevent large data files from being committted.

## To-Do's

- Upgrade to data streaming for high data-rates (>15Hz)
- Clean up code
