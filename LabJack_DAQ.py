# Ay191_DAQ.py
# DPV 2/9/17
# Python code to be used for reading DMM (Agilent 34410A)
# and digital incinometer (both via USB) for beam mapping
# operates on unix systems

# JAC 28 Nov 2017
# Code has been modified for a U6 Labjack

# stop deprecation warning from plt.pause()
import warnings
warnings.filterwarnings("ignore")

# import other packages
#import usbtmc
import time
import datetime
import matplotlib.pyplot as plt
import serial
import csv
#from labjack import u6
import u6
import sys
try:
  from matplotlib import animation
except ImportError:
  import animation


import numpy as np
import os
import select
import argparse



###############################################

# Subfunction for data recording and logging.

def getData(num, arr, line):
  # get dmm voltage
  # volt = float(dmm.ask(":MEAS:VOLT:DC?"))
  #os.system('cls' if os.name == 'nt' else 'clear')
  global a, el_time, proc_start, count, ch
  global volt, time_data, l1, avg, b, d, fieldnames
  if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
    cmd = raw_input()
    if cmd == 'stop':
      exit()
    elif cmd == 'pause':
      cmd = raw_input('DAQ paused. Press Enter to continue or enter stop to quit.')
    #elif avg == False:
    #  b = np.zeros((1,3))
    #  avg = True
    #  print("Starting integration")
    #  #note_string = "avging"
    #else:
    #  avg = False
    #  b_mean = np.mean(b[1:,1], axis=0)
    #  b_err = np.sqrt(np.var(b[1:,1], axis=0)/len(b[1:,2]))
    #  b_mean2 = np.mean(b[1:,2], axis=0)
    #  b_err2 = np.sqrt(np.var(b[1:,2], axis=0)/len(b[1:,2]))
    #  print("Samples: {4}\nMean_1: {0}, Err on Mean_1: {1}\nMean_2: {2}, Err on Mean_2: {3}".format(b_mean, b_err, b_mean2, b_err2, len(b[1:,2])))
     #del note_string
  
  #realtime = datetime.datetime.now() - time_start
  


  
  volt = np.zeros(len(ch.split(',')))
  samp_el = 0
  count = 0
  tstart = time.time()
  while samp_el < 1/sr:
    v = read_volts(len(ch.split(',')))
    volt = volt + np.array(v)
    #rt = datetime.datetime.now() - time_start
    samp_el = time.time()-tstart
    count = count+1

  v = volt/count
  v = v.tolist()
  el_time = time.time()
  time_data = el_time
  #volt = sum(volt)/len(volt)
  #volt2 = sum(volt2)/len(volt2)
  #v = read_volts(len(ch.split(',')))
  if avg:
    avging = 1
  else:
    avging = 0

  # get digital protractor angle
  #ser.flushInput()
  #time.sleep(0.1)
  #angle_str = ser.readline()
  #angle_str = angle_str.split()
  #inc_angle = FindAngle(angle_str)
  
  # plot voltage vs Time
  z = [el_time]
  z2 = "{0}".format(el_time)
  for i in range(0,len(ch.split(','))):
    z.append(v[i])
    z2 = z2+",{0}".format(v[i])
  #z.append(avging)
  z2 = z2+",{0}".format(avging)
  #print z2
  inc = 1
  #line.clear()

  if avg:
    b = np.append(b, z, axis=0)
    if PLOT == True:
      a = np.append(a, z[0:len(z)-1], axis=0)
      line.plot(a[1:, 0], a[1:, 1], '.g',  b[1:, 0], b[1:, 1], '.r')
      line2.plot(a[1:, 0], a[1:, 2], '.y', b[1:, 0], b[1:, 2], '.b')
  else:
    if PLOT == True:
      a = np.append(a, [z], axis=0)
      line.plot(a[1:, 0], a[1:, 1], '.g')
      #line2.plot(a[1:, 0], a[1:, 2], '.y')
  # save data in text and csv format
  if note_string:
    #f.write("%s\t%.6f\t%s\n" %(datetime.datetime.now(),volt,note_string))
    with open(filenamex,'a') as csvfile:
      #fieldnames = ['Time','DMM_volt','volt2','avging_on', 'Notes']
      #writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
      z2 = z2+","+note_string
      csvfile.writelines(z2)
      csvfile.write("\n")
  else:
    #f.write("%s\t%.6f\n" %(datetime.datetime.now(),volt))
    with open(filenamex,'a') as csvfile:
      #fieldnames = ['Time','DMM_volt','volt2','avging_on']
      #writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
      #writer.writerow(z)
      csvfile.writelines(z2)
      csvfile.write("\n")
  return line,
	  
###############################################

def run_ani():
    global a, ch
    
    fig1 = plt.figure()


    time = 10
    a = np.zeros((1,len(ch.split())+1))
    #print a
    l = fig1.add_subplot(1,1,1)
    l.set_xlabel("Time (s)")
    l.set_ylabel(ylab)

    # l2 = fig1.add_subplot(2,1,2)
    # l2.set_xlabel("Time (s)")
    # l2.set_ylabel(ylab)

    try:
      fig1_ani = animation.FuncAnimation(fig1, getData, 100, fargs=(a, l), interval=50, blit=False)
    except KeyboardInterrupt:
      pass
    return plt.show()

def get_field_names(ch, inc):
  S = ch.split(',')
  fld_name = ["Time"]
  if inc: #If inclinometer is toggled on, put that first.
    fld_name.append(",Angle")
  for i in range(0,len(S)): #Add channel names
    fld_name.append(",{0}".format(S[i]))

  fld_name.append(",avging_on")
  #fld_name.append(",Notes")
  return fld_name

def read_volts(ch):
  v = []
  for i in range(0,int(ch)):
    v.append(adc.getAIN(i))
  return v

def get_args():
  parser = argparse.ArgumentParser(description = 'Logs and plots timestream of data with various options')
  parser.add_argument("--temp", nargs = 2, default = (0,0), help = "Hot/cold load power value (NOT WORKING)", type=float)
  parser.add_argument("--title", help = "Change the default filename. def = {0}".format(def_filenamex), default = def_filenamex)
  parser.add_argument("--plot", help = "Toggles plotting feature. (Normally off)", default = False, action = "store_true")
  #parser.add_argument("--rx", help = "RX name in filename", default = def_rx, type = int)
  #parser.add_argument("--el", help = "el in filename", default = def_el, type = float)
  parser.add_argument("--dir", help = "dir in filename", default = def_dir)
  parser.add_argument("--ch", help = "Select number of channels up to 13 by naming them. E.g. \"T,V,T2,V2\" (for labjack only)", default= "AIN0")
  parser.add_argument("--inc", help="Toggle acquisition from digital inclinometer (normally off)", default=False, action="store_true")
  parser.add_argument("--sr", help="Set sample rate in samps / sec (only when not plotting) Default = 1", default=1.0, type = float)
  return parser, parser.parse_args()

# Main function
if __name__ == '__main__':
  # initialize params
  avg = False
  volt = []
  el_time = []

  def_dir = "~/LabJackDaq/data"

  def_filenamex ="labjack_generic_daq.csv".format(def_dir, datetime.datetime.now())
  parser, args = get_args()
  filenamex ='{1}/{0}.csv'.format(args.title, args.dir)
  
  # Check if filename exists and append a number to the end of it
  if os.path.isfile(filenamex):
    run_num = 0
    print "File: {0} already exists!".format(args.title)
    while os.path.isfile(filenamex):
      run_num = run_num+1
      filenamex = "{1}/{0}_{2}.csv".format(args.title,args.dir,run_num)
  
  ch = args.ch
  sr = args.sr
  PLOT = args.plot
  inc = args.inc
  #Initialize DAQ
  adc = u6.U6()
  adc.getCalibrationData()

  if inc:
    ser = serial.Serial("/dev/ttyUSB0", baudrate=9600);
    ser.close()
    ser.open()


    # Cycle power if digital protractor freezes up
    print('Cycle Digital Protractor Power to Continue:\n')
    ser.readline()
    ser.readline()

  if (args.temp[1] > 0):
      p1, p2, t1, t2 = float(sys.argv[1]), float(sys.argv[2]), 300, 77.6
      gain = (p1-p2)/(t1-t2)
      ylab = "Temp (K)"
  else:
      gain = 1
      ylab = "Voltage (V)"

  #open csvfile
  with open(filenamex,'w') as csvfile:
    fieldnames = get_field_names(args.ch, inc)
    #writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #writer.writeheader()
    csvfile.writelines(fieldnames)
    csvfile.write("\n")
    print "Writing data to file: {0}".format(filenamex)
  #print input commands
  print("input enter key to take data point OR input integer for multiple points")
  print("input 'auto' to continously log data, stop with keyboard interrupt")
  print("input 'stop' to stop taking data and close recorder")
  #print("input 'note' to then enter in a note string to be attached to a data point")

  #generate empty note_string
  note_string = []

  # main function loop
  while(1):

    # ask for input, stop if requested
    input_string = raw_input()
    time_start = time.time()
    if input_string == 'stop':
      #f.close()
      break

    # check for multi-measurement request
    try:
      burst = int(input_string)-1
      while(burst > 0):
        burst = burst - 1
        getData()
        if PLOT == True:
          plt.pause(0.001)
          time.sleep(0.1)
    except ValueError:
      pass

    # check for auto-measurement request
    if input_string == 'auto':
      print "Starting data aquisition...\n"
      print "Enter pause to temporarily stop DAQ or enter stop to close program."
      try:
        #while(1):
        #getData()
        
        if PLOT == True:
          run_ani()
          plt.show()
          plt.pause(0.001)
          #time.sleep(0.1)
        else:
          while(1):
            getData([],[],[])
      except KeyboardInterrupt:
        pass

    if input_string == 'note':
      note_string = input()

    # make a measurement
    #getData()


