# -*- coding: utf-8 -*-
"""
This example demonstrates the use of pyqtgraph's dock widget system.

The dockarea system allows the design of user interfaces which can be rearranged by
the user at runtime. Docks can be moved, resized, stacked, and torn out of the main
window. This is similar in principle to the docking system built into Qt, but
offers a more deterministic dock placement API (in Qt it is very difficult to
programatically generate complex dock arrangements). Additionally, Qt's docks are
designed to be used as small panels around the outer edge of a window. Pyqtgraph's
docks were created with the notion that the entire window (or any portion of it)
would consist of dockable components.

"""

# import initExample ## Add path to library (just for examples; you do not need this)

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.console
import numpy as np
import argparse
import os.path as op
import glob
import time

from pyqtgraph.dockarea import *

import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

global filenamex, pltlist, d1
global area, params, ptree, timer


# Load data
###############################################
def load_data():
    data = np.genfromtxt(filenamex, delimiter=',', names=True)
    return data


# Options for the arg-parser
###############################################
def get_args():
    parser = argparse.ArgumentParser(description='Plots timestream of data with various options')
    parser.add_argument("--title", help="Choose a filename. Defaults to newest csv in directory", default=def_filenamex)
    parser.add_argument("--dir", help="dir in filename", default=def_dir)
    parser.add_argument("--refrate", help="Set refresh rate in milliseconds. Default = 50ms", default=50,
                        type=float)
    parser.add_argument("--pm", help="Dual-channel reading. I.e. Ch0=V+, Ch1=V-, plots V+ + V-  (Normally off)",
                        default=False, action="store_true")
    return parser, parser.parse_args()


def update():
    data = load_data()
    data[data.dtype.names[0]] -= data[data.dtype.names[0]][0]
    for plt in pltlist:
        plt.update(data)


def timer_control(param, value):
    global timer, refrate
    if not value:
        timer.stop()
    elif not timer.isActive():
        timer.start(refrate)


# Make a plotter class
class Plotter():
    def __init__(self, chname):
        global area, params, ptree
        self.name = chname
        self.d = Dock(chname, size=(500, 200))
        self.w = pg.PlotWidget()
        self.curve = self.w.plot()
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
            self.curve.setData(data[data.dtype.names[0]][-N:], data[self.name][-N:])
        else:
            self.curve.setData(data[data.dtype.names[0]], data[self.name])


## Make the app
app = QtGui.QApplication([])
win = QtGui.QMainWindow()
area = DockArea()
win.setCentralWidget(area)
win.resize(1200, 500)
win.setWindowTitle('LabJack Live Plot')

## Create docks, place them into the window one at a time.
## Note that size arguments are only a suggestion; docks will still have to
## fill the entire dock area and obey the limits of their internal widgets.

# Make initial parameters
p = {'name': "Main",
     'type': 'group',
     'children': [
         {'name': 'AutoUpdate', 'type': 'bool', 'value': True},
         {'name': 'Update', 'type': 'action'},
     ]
     }

## Make parameter tree widget
param_dock = Dock("Plot Params", (200, 400))
ptree = ParameterTree()
param_dock.addWidget(ptree)

params = Parameter.create(name='params', type='group', children=[])
params.addChild(p)

params.param('Main', 'Update').sigActivated.connect(update)
params.param('Main', 'AutoUpdate').sigValueChanged.connect(timer_control)

win.show()

timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':

    # Set up argument parser
    def_dir = op.join(op.expanduser("~"), "LabJackDAQ", "data")
    def_filenamex = ""
    parser, args = get_args()
    refrate = args.refrate
    pm = args.pm

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

    csvfile = open(filenamex, 'r')
    # print(csvfile.readline())
    global test_data
    # test_data = np.genfromtxt([csvfile.readline()],delimiter=',',names=True)
    # test_dnames = test_data.dtype.names

    test_data = np.random.normal(0, 1, (5, 1))

    # Set up the plots automatically
    area.addDock(param_dock)
    data = load_data()
    dnames = data.dtype.names

    pltlist = [Plotter(chname) for chname in dnames[1:-1]]
    area.moveDock(pltlist[-1].d, "right", param_dock)
    for p in pltlist[0:-1]:
        area.moveDock(p.d, "top", pltlist[-1].d)

    import sys

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
