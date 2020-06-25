# Ay191_DAQ.py
# DPV 2/9/17
# Python code to be used for reading DMM (Agilent 34410A)
# and digital incinometer (both via USB) for beam mapping
# operates on unix systems

# JAC 06 Sep 2019
# Code has been modified for a U6 Labjack and cleaned up a bit

# import other packages
import usbtmc
import time
import datetime
import serial
import u6
import numpy as np
import os.path as op
import argparse
from threading import Thread

# Global Variables
thstat = True

# Wrapper function for threading.
###############################################
def auto_daq(ch,dmmtype,csvfile):
    global thstat
    while thstat:
        el_time, v, inc_angle, avging = get_data(ch,dmmtype)
        fstring = write_data(csvfile, el_time, v, inc_angle, avging)
    return


# Subfunction for data recording and logging.
###############################################
def get_data(ch, dmmtype):
    # If loop runs faster than the sample rate, average until enough time elapses
    global dmm, data_array
    volt = np.zeros(len(ch.split(',')))
    samp_el = 0
    count = 0
    tstart = time.time()
    while samp_el < 1 / sr:
        v = read_volts(len(ch.split(',')),dmmtype)
        volt = volt + np.array(v)
        # rt = datetime.datetime.now() - time_start
        samp_el = time.time() - tstart
        count = count + 1

    v = volt / count
    v = v.tolist()
    el_time = time.time()

    if avg:
        avging = 1
    else:
        avging = 0

    # get inclinometer angle
    inc_angle = []
    if inc:
        ser.flushInput()
        time.sleep(0.1)
        angle_str = ser.readline()
        angle_str = angle_str.split()
        inc_angle = findangle(angle_str)

    return el_time, v, inc_angle, avging


# Convert numbers into a comma-separated line and append it to our csv file
###############################################
def write_data(csvfile, time, volts, angle, avging):
    fs = "{0}".format(time) # Filestring

    # If Inclinometer is on, put that first.
    if angle:
        fs = fs + ",{0}".format(angle)

    for i in range(0,len(volts)):
        fs = fs + ",{0}".format(volts[i])

    fs = fs + ",{0}".format(avging)

    # save data in text and csv format

    csvfile.writelines(fs)
    csvfile.write("\n")
    csvfile.flush()
    return fs

# Determine the field names that go into the csv
###############################################
def get_field_names(ch, inc):
    s = ch.split(',')
    fld_name = ["Time"]
    if inc:  # If inclinometer is toggled on, put that first.
        fld_name.append(",Angle")
    for i in range(0, len(s)):  # Add channel names
        fld_name.append(",{0}".format(s[i]))

    fld_name.append(",avging_on")
    return fld_name

# Get values from the dmm
###############################################
def read_volts(ch, dmmtype):
    global dmm
    v = []
    if dmmtype == "u6":
        if diff:
            di = 2
            iend = int(ch)*2
        else:
            di = 1
            iend = int(ch)

        for i in range(0, iend,di):
            try:
                v.append(dmm.getAIN(i,differential=diff))
            except:
                print("Got zero packet")
                dmm.close()
                time.sleep(0.5)
                dmm = u6.U6()
                dmm.getCalibrationData()
                #v.append(dmm.getAIN(i,differential=diff))
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
    parser.add_argument("--sr", help="Set sample rate in samps / sec (only when not plotting) Default = 1", default=1.0,
                        type=float)
    parser.add_argument("--ow", help="Overwrite input file. (Normally off)",
                        default=False, action="store_true")
    parser.add_argument("--diff", help="Take Differential readings. Pos input on even channels, negative on input channel+1 (Normally off)",
                        default=False, action="store_true")
    return parser, parser.parse_args()


###############################################
def print_menu():
    print("##########")
    print("##########")
    print("input enter key to take a single data point")
    print("input 'auto' to continuously log data")
    print("input 'stop' to stop taking data and close recorder")
    print("##########")
    print("##########")
    return


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
    with open(filenamex, 'w') as csvfile:
        fieldnames = get_field_names(args.ch, inc)

        csvfile.writelines(fieldnames)
        csvfile.write("\n")
        csvfile.flush()
        csvfile.close()
        print("Writing data to file: {0}".format(filenamex))

    csvfile = open(filenamex,'a')

    # Initialize inclinometer if wanted
    if inc:
        ser = serial.Serial("/dev/ttyUSB0", baudrate=9600);
        ser.close()
        ser.open()

        # Cycle power if digital protractor freezes up
        print('Cycle inclinometer power to Continue:\n')
        ser.readline()
        ser.readline()

    runprog = True
    # main function loop
    while runprog:
        # print input commands
        print_menu()
        # ask for input, stop if requested
        input_string = input()

        # If they just hit enter, collect one data point.
        if not input_string:
            fs = get_data(args.ch, dmmtype)
            print(fs)
        if input_string == 'stop':
            runprog = False

        # # check for multi-measurement request
        # try:
        #     burst = int(input_string)
        #     while (burst > 0):
        #         fs = get_data(args.ch, dmmtype)
        #         print(fs)
        #         burst = burst - 1
        # except ValueError:
        #     pass

        # check for auto-measurement request
        if input_string == 'auto':
            thstat = True
            print("Starting data aquisition...\n")
            print("Enter pause to temporarily stop DAQ or enter stop to close program.")
            # Initialize DAQ loop
            daqthread = Thread(target=auto_daq, args=(args.ch, dmmtype, csvfile,))
            daqthread.start()

            cmd = input()
            if cmd == 'stop':
                thstat = False
                runprog = False
            elif cmd == 'pause':
                thstat = False
            else:
                print("Command not recognized. Try again. (DAQ still running)")
