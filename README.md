# LabJackDAQ


## Functions

This includes two primary functions, `LabJack_DAQ.py` and `plt_data.py`

Check the help for more info (i.e. `python LabJack_DAQ.py --help`)

## Shortcutting:

After installation, add these aliases to your `.bashrc`:

```
alias ljdaq='python ~/LabJackDAQ/LabJack_DAQ.py'
alias dataplot='python ~/LabJackDAQ/plt_data.py'
```

That way, you can start the data acquisition from any directory and it should still work, provided you've done the shortcuts correctly.

## Notes
- The data folder is for local use only. There's a `gitignore` that excludes `.csv` files to prevent large data files from being committted.

## To-Do's

- Upgrade to data streaming for high data-rates (>15Hz)
- Clean up code
