# plt_data.py
# JAC 20190904
# plots data from csv files
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os.path as op
import glob

# Global Variables
runloop = True
Ntail = 0


# Options for the arg-parser
###############################################
def get_args():
    parser = argparse.ArgumentParser(description='Plots timestream of data with various options')
    parser.add_argument("--title", help="Choose a filename. Defaults to newest csv in directory", default=def_filenamex)
    parser.add_argument("--dir", help="dir in filename", default=def_dir)
    parser.add_argument("--refrate", help="Set refresh rate in seconds. Default = manual", default=0,
                        type=float)
    return parser, parser.parse_args()


# Main plotting function. Reloads data, then plots all available channels.
###############################################
def do_plots(filename, ntail, figure):
    data = load_data(filename)
    dnames = data.dtype.names
    t = dnames[0]
    tn = data[t]
    tn -= tn[0]
    plen = len(dnames) - 2
    fig.clf()
    axes = fig.subplots(plen, 1, squeeze=False)

    for i in range(1, plen+1):
        dn = data[dnames[i]]
        if plen==1:
            ax = axes
        else:
            ax = axes[i-1]

        if ntail == 0:
            ax.plot(tn, dn)
        else:
            ax.plot(tn[-ntail:], dn[-ntail:])

        ax.set_title(dnames[i])
        ax.grid(True)
        ax.figure.canvas.draw()

    plt.xlabel('Time (s)')
    plt.subplots_adjust(hspace=1.2)
    ax.figure.canvas.draw()


# Load data
###############################################
def load_data(filename):
    data = np.genfromtxt(filename, delimiter=',', names=True)
    return data


# Print the menu
###############################################
def print_menu(refreshrate):

    print("##########")
    print("##########")

    if refreshrate == 0:
        print("input enter key to refresh OR input integer to plot last N points")

    else:
        print("input 'pause' to pause OR input integer to plot last N points")

    print("input 'all' or '0' to plot all data")
    print("input 'quit' to close")
    print("##########")
    print("##########")
    return


# Handle inputs from the terminal
###############################################
def input_func(timer, lpcount):
    global runloop, callon, Ntail, paused
    input_string = input()

    if input_string == "all":
        Ntail = 0
    elif input_string == "quit":
        runloop = False
        print("Complete!")
    elif input_string == "pause":
        paused = True
        print("Plotting paused. Enter 'resume' to continue.")
    elif input_string == "resume":
        paused = False
    elif not input_string == "":
        try:
            Ntail = int(input_string)
            if Ntail < 0:
                Ntail = abs(Ntail)

            if Ntail == 8675309:
                Ntail = 0
                for i in range(0,100):
                    print("Jenny, I've got your number!")

            print("Loading the last {0} points...".format(Ntail))
        except ValueError:
            print("Input not recognized. Try again.")

    if callon:
        timers[loopcount].stop()
        callon = False


# Main Program
###############################################
if __name__ == '__main__':
    # Set up argument parser
    def_dir = op.join(op.expanduser("~"), "LabJackDAQ", "data")
    def_filenamex = ""
    parser, args = get_args()
    refrate = args.refrate

    # File handling stuff
    if args.title == "":
        lof = glob.glob(op.join(args.dir, "*.csv"))
        if len(lof) > 0:
            args.title = max(lof, key=op.getmtime)
            filenamex = '{0}'.format(args.title)
        else:
            raise NameError("No CSV files found in {0}".format(args.dir))
    else:
        if not args.title[-4::] == ".csv":
            args.title = args.title + ".csv"
        filenamex = op.join(args.dir, args.title)

    # Check if filename exists
    if not op.isfile(filenamex):
        raise NameError("File: {0} doesn't exist!".format(args.title))
    else:
        print("Loading: {0}".format(filenamex))

    # Init some variables and start plotting.
    fig = plt.figure(1)
    plt.show(block=False)
    runloop = True
    paused = False
    callon = False
    loopcount = 0
    timers = []
    while runloop:
        if not paused:
            # I can't figure out an easy way to remove a timer from a canvas. The current workaround is to stop the old
            # timer and create a new timer so multiple instances of do_plots don't start running.
            timers.append(fig.canvas.new_timer(interval=int(refrate * 1000)))
            if refrate > 0:
                timers[loopcount].add_callback(do_plots, filenamex, Ntail, fig)
                callon = True
                timers[loopcount].start()

            else:
                do_plots(filenamex, Ntail, fig)
            print_menu(refrate)
            addto = 1
        else:
            addto = 0
        input_func(timers, loopcount)
        loopcount += addto
