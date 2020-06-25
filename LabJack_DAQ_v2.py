# Ay191_DAQ.py
# DPV 2/9/17
# Python code to be used for reading DMM (Agilent 34410A)
# and digital incinometer (both via USB) for beam mapping
# operates on unix systems

# JAC 06 Sep 2019
# Code has been modified for a U6 Labjack and cleaned up a bit

# JAC 25 Jun 2020
# Major overhaul to the code.
# Now uses PyQtGraph for plotting and Pandas for data handling.

# import other packages
import usbtmc
import time
import datetime
import serial
import u6
import numpy as np
import os.path as op
import argparse
import sys
import pandas as pd
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import *
from pyqtgraph.parametertree import Parameter, ParameterTree

global filenamex, pltlist
global area, params, ptree, timer
global args


# Subfunction for data recording and logging.
###############################################
def get_data():
    # If loop runs faster than the sample rate, average until enough time elapses
    global args, daq_data, dmmtype
    data_row = []
    volt = np.zeros(len(args.ch.split(',')))
    samp_el = 0
    count = 0
    tstart = time.time()
    while samp_el < 1 / sr:
        v = read_volts(len(args.ch.split(',')), dmmtype)
        volt = volt + np.array(v)
        # rt = datetime.datetime.now() - time_start
        samp_el = time.time() - tstart
        count = count + 1

    v = volt / count
    v = v.tolist()
    # el_time = time.time()
    data_row.append(time.time())
    data_row[1:1] = v

    # get inclinometer angle
    # inc_angle = []
    if args.inc:
        ser.flushInput()
        time.sleep(0.1)
        angle_str = ser.readline()
        angle_str = angle_str.split()
        # inc_angle = findangle(angle_str)
        data_row.append(findangle(angle_str))

    if avg:
        data_row.append(1)
    else:
        data_row.append(0)

    daq_data = daq_data.append(pd.DataFrame([data_row],
                                            columns=daq_data.keys().to_list()),
                               ignore_index=True)

    # return el_time, v, inc_angle, avging


# Determine the field names that go into the csv
###############################################
def get_field_names(ch, inc, commas=True):
    cm = ""
    if commas:
        cm = ","

    s = ch.split(',')
    fld_name = ["Time"]
    if inc:  # If inclinometer is toggled on, put that first.
        fld_name.append(cm + "Angle")
    for i in range(0, len(s)):  # Add channel names
        fld_name.append(cm + "{0}".format(s[i]))

    fld_name.append(cm + "avging_on")
    return fld_name


# Get values from the dmm
###############################################
def read_volts(ch, dmmtype):
    global dmm
    v = []
    if dmmtype == "u6":
        if diff:
            di = 2
            iend = int(ch) * 2
        else:
            di = 1
            iend = int(ch)

        for i in range(0, iend, di):
            try:
                v.append(dmm.getAIN(i, differential=diff))
            except:
                print("Got zero packet")
                dmm.close()
                time.sleep(0.5)
                dmm = u6.U6()
                dmm.getCalibrationData()
                v.append(np.nan)

    elif dmmtype == "agil":
        v = float(dmm.ask(":MEAS:VOLT:DC?"))
    elif dmmtype == "test":
        for i in range(0, int(ch)):
            v.append(np.random.randn())
    else:
        raise ValueError("Acquisition Type not recognized.")
    return v


###############################################
# Subfunction for extracting angle from inclinometer
# (convert ascii text to float)
def findangle(angle_str):
    angle = 0
    if angle_str:
        if angle_str[0] == b'+':
            angle_sign = 1
            angle = -1 * angle_sign * float(angle_str[1])
        if angle_str[0] == b'-':
            angle_sign = -1
            angle = -1 * angle_sign * float(angle_str[1])
        if len(angle_str) == 1:
            angle = -1 * float(angle_str[0])
    else:
        angle = 0
    return angle


###############################################
def get_args():
    parser = argparse.ArgumentParser(description='Logs and plots timestream of data with various options')
    parser.add_argument("--temp", nargs=2, default=(0, 0), help="Hot/cold load power value (NOT WORKING)", type=float)
    parser.add_argument("--title", help="Change the default filename. def = {0}".format(def_filenamex),
                        default=def_filenamex)
    parser.add_argument("--dmm", help="Utilize Agilent DMM instead of U6 for DAQ, only 1 channel. (Normally off)",
                        default=False, action="store_true")
    parser.add_argument("--test", help="Disables DAQs and writes fake data for testing. (Normally off)",
                        default=False, action="store_true")
    parser.add_argument("--dir", help="dir in filename", default=def_dir)
    parser.add_argument("--ch",
                        help="Select number of channels up to 13 by naming them. E.g. \"T,V,T2,V2\" (for labjack only)",
                        default="AIN0")
    parser.add_argument("--inc", help="Toggle acquisition from digital inclinometer (normally off)", default=False,
                        action="store_true")
    parser.add_argument("--sr", help="Set sample rate in samps / sec (only when not plotting) Default = 50", default=50.0,
                        type=float)
    parser.add_argument("--ow", help="Overwrite input file. (Normally off)",
                        default=False, action="store_true")
    parser.add_argument("--diff",
                        help="Take Differential readings. Pos input on even channels, negative on input channel+1 (Normally off)",
                        default=False, action="store_true")
    return parser, parser.parse_args()


###############################################
# GUI STUFF
def update():
    global daq_data
    for plt in pltlist:
        plt.update(daq_data)


def daq_toggle(param, value):
    global daq_timer
    timer_control(daq_timer, value, 1 / args.sr)


def plot_toggle(param, value):
    global plot_timer
    timer_control(plot_timer, value, 50)


def contrast_toggle(param, value):
    global pltlist, params
    if value:
        for plt in pltlist:
            plt.w.setBackground('k')
            # plt.curve.getViewBox().setBackgroundColor('k')
            params.param(plt.name, 'Color').setValue((0, 200, 255))
            plt.w.showGrid(x=True, y=True)
    else:
        for plt in pltlist:
            clr = (255, 255, 255)
            plt.w.setBackground('w')
            # plt.curve.getViewBox().setBackgroundColor('w')
            params.param(plt.name, 'Color').setValue((0, 0, 255))
            plt.w.showGrid(x=True, y=True)


def autosave_toggle(param, value):
    global save_timer, params
    timer_control(save_timer,
                  value,
                  params['DAQ Options', 'AutoSave Options', 'Save Interval (Min)'] * 60 * 1000)


def set_autosave(param, value):
    global save_timer, params
    if params['DAQ Options', 'AutoSave Options', 'AutoSave']:
        save_timer.setInterval(value * 60 * 1000)


def timer_control(param, value, sr):
    if not value:
        param.stop()
    elif not param.isActive():
        param.start(sr)


def save_csv():
    global filenamex, daq_data
    daq_data.to_csv(filenamex)


def change_file(param, value):
    global filenamex
    filenamex = value


def make_options():
    global filenamex
    params = Parameter.create(name='params', type='group', children=[])

    ## DAQ Options
    params.addChild(
        {'name': "DAQ Options",
         'type': 'group',
         'children': [
             {'name': 'AutoDAQ', 'type': 'bool', 'value': True},
             {'name': 'Get Datapoint', 'type': 'action'},
             {'name': 'Save Location', 'type': 'text', 'value': filenamex},
             {'name': 'Save', 'type': 'action'},
             {'name': 'AutoSave Options', 'type': 'group', 'children': [
                 {'name': 'AutoSave', 'type': 'bool', 'value': True},
                 {'name': 'Save Interval (Min)', 'type': 'float', 'value': '10'}
             ]},
         ]
         }
    )

    params.param('DAQ Options', 'Get Datapoint').sigActivated.connect(get_data)
    params.param('DAQ Options', 'AutoDAQ').sigValueChanged.connect(daq_toggle)
    params.param('DAQ Options', 'Save Location').sigValueChanged.connect(change_file)
    params.param('DAQ Options', 'Save').sigActivated.connect(save_csv)
    params.param('DAQ Options', 'AutoSave Options', 'Save Interval (Min)').sigValueChanged.connect(set_autosave)
    params.param('DAQ Options', 'AutoSave Options', 'AutoSave').sigValueChanged.connect(autosave_toggle)
    ## Plot Options
    params.addChild(
        {'name': "Plot Options",
         'type': 'group',
         'children': [
             {'name': 'AutoUpdate', 'type': 'bool', 'value': True},
             {'name': 'Update', 'type': 'action'},
             {'name': 'High Contrast Mode', 'type': 'bool', 'value': True},
         ]
         })

    params.param('Plot Options', 'Update').sigActivated.connect(update)
    params.param('Plot Options', 'AutoUpdate').sigValueChanged.connect(plot_toggle)
    params.param('Plot Options', 'High Contrast Mode').sigValueChanged.connect(contrast_toggle)
    return params


# Make a plotter class
class Plotter():
    def __init__(self, chname):
        global area, params, ptree
        self.name = chname
        self.d = Dock(chname, size=(500, 300))
        self.w = pg.PlotWidget()
        self.curve = self.w.plot()
        self.w.showGrid(x=True, y=True)
        self.w.setTitle(chname)
        self.d.addWidget(self.w)

        area.addDock(self.d, 'bottom')

        self.params = Parameter.create(name=chname, type='group', children=[
            {'name': 'Color', 'type': 'color', 'value': "0CC", 'tip': "This is a color button"},
            {'name': 'Scrolling', 'type': 'group', 'expanded': False, 'children': [
                {'name': 'Scrolling', 'type': 'bool', 'value': False},
                {'name': 'Range (samples)', 'type': 'int', 'value': 300},
            ]}

        ])

        params.addChild(self.params)
        ptree.setParameters(params, showTop=False)

        return

    def update(self, data):
        self.curve.setPen(self.params['Color'].getRgb())

        if self.params['Scrolling', 'Scrolling']:
            N = self.params['Scrolling', 'Range (samples)']
            self.curve.setData(data[data.keys().to_list()[0]].iloc[-N:].values, data[self.name].iloc[-N:].values)
        else:
            self.curve.setData(data[data.keys().to_list()[0]], data[self.name])


class MainWindow(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi()

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(277, 244)
        self.statusbar = QtGui.QStatusBar()
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

    def closeEvent(self, event):
        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)

        msg.setText("Are you sure you want to exit?")
        msg.setInformativeText("Your data will be save to")
        msg.setWindowTitle("")
        msg.setDetailedText(filenamex)
        msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        # msg.buttonClicked.connect(msgbtn)

        retval = msg.exec_()
        print
        "value of pressed message box button:", retval

        event.ignore()

        if retval == QtGui.QMessageBox.Ok:
            save_csv()
            event.accept()


## Make the app
app = QtGui.QApplication([])
win = MainWindow()
area = DockArea()
win.setCentralWidget(area)
win.resize(1200, 900)
win.setWindowTitle('LabJack Live Plot')

## Create docks, place them into the window one at a time.
## Note that size arguments are only a suggestion; docks will still have to
## fill the entire dock area and obey the limits of their internal widgets.

## Make parameter tree widget
param_dock = Dock("Settings", (200, 900))
ptree = ParameterTree()
param_dock.addWidget(ptree)

win.show()

plot_timer = pg.QtCore.QTimer()
plot_timer.timeout.connect(update)
plot_timer.start(50)

daq_timer = pg.QtCore.QTimer()
daq_timer.timeout.connect(get_data)
daq_timer.start(1)

save_timer = pg.QtCore.QTimer()
save_timer.timeout.connect(save_csv)
save_timer.start(10 * 60 * 1000)
###############################################
# Main function
if __name__ == '__main__':
    # initialize params
    avg = False

    def_dir = op.join(op.expanduser("~"), "LabJackDAQ", "data")
    def_filenamex = "labjack_generic_daq.csv".format(def_dir, datetime.datetime.now())
    parser, args = get_args()

    sr = args.sr
    inc = args.inc
    diff = args.diff
    # Initialize DAQ
    # Prioritize test option, then Agilent DMM, and lastly the LabJack.
    if args.test:
        dmmtype = "test"
    else:
        if args.dmm:
            dmmtype = "agil"
            dmm = usbtmc.Instrument(2391, 1543)
            dmm.ask("*IDN?")
        else:
            dmmtype = "u6"
            dmm = u6.U6()
            dmm.getCalibrationData()

    # File management:
    if args.title[-4::] == ".csv":
        args.title = args.title[0:-4]

    filenamex = op.join(args.dir, args.title + ".csv")
    # Check if filename exists. Overwrite or append a number to the end of it to make it unique.
    if op.isfile(filenamex) and not args.ow:
        run_num = 0
        print("File: {0} already exists!".format(args.title))
        while op.isfile(filenamex):
            run_num = run_num + 1
            filenamex = op.join(args.dir, args.title + "{0}.csv".format(run_num))
        print("Using file: " + filenamex)

    # Open csvfile
    fieldnames = get_field_names(args.ch, inc)
    with open(filenamex, 'w') as csvfile:
        csvfile.writelines(fieldnames)
        csvfile.write("\n")
        csvfile.flush()
        csvfile.close()
        print("Writing data to file: {0}".format(filenamex))

    csvfile = open(filenamex, 'a')
    fields = get_field_names(args.ch, inc, commas=False)
    daq_data = pd.DataFrame(columns=fields)

    params = make_options()

    # Set up the plots automatically
    area.addDock(param_dock)

    pltlist = [Plotter(chname) for chname in fields[1:-1]]
    area.moveDock(pltlist[-1].d, "right", param_dock)
    for p in pltlist[0:-1]:
        area.moveDock(p.d, "top", pltlist[-1].d)

    # Initialize inclinometer if wanted
    if inc:
        ser = serial.Serial("/dev/ttyUSB0", baudrate=9600);
        ser.close()
        ser.open()

        # Cycle power if digital protractor freezes up
        print('Cycle inclinometer power to Continue:\n')
        ser.readline()
        ser.readline()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
