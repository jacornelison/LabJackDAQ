# plt_data.py
# JAC 20190904
# plots data from LabJack_DAQ.py
import matplotlib.pyplot as plt
import numpy as np
import time
import argparse
import datetime
import os.path as op
import glob

def get_args():
  parser = argparse.ArgumentParser(description = 'Plots timestream of data with various options')
  parser.add_argument("--title", help = "Choose a filename. Defaults to newest csv in directory", default = def_filenamex)
  parser.add_argument("--dir", help = "dir in filename", default = def_dir)
  parser.add_argument("--ch", help = "Select number of channels up to 13 by naming them. E.g. \"T,V,T2,V2\" (for labjack only)", default= "AIN0")
  return parser, parser.parse_args()

# Main Program
if __name__ == '__main__':
  def_dir = op.join(op.expanduser("~"),"LabJackDAQ","data")
  def_filenamex = ""
  parser, args = get_args()


  if args.title=="":
    lof = glob.glob(op.join(args.dir,"*.csv"))
    if len(lof)>0:
      args.title = max(lof, key=op.getmtime)
      filenamex = '{0}'.format(args.title)
    else:
      raise NameError("No CSV files found in {0}".format(args.dir))
  else:
    if not args.title[-4::] == ".csv":
      args.title = args.title+".csv"
    filenamex = op.join(args.dir, args.title)

  # Check if filename exists
  if not op.isfile(filenamex):
    raise NameError("File: {0} doesn't exist!".format(args.title))
  else:
    print "Loading: {0}".format(filenamex)

  Ntail = 0
  fig = plt.figure()
  plt.interactive(False)
  while True:

    # Data will be format: rows = samples, columns = channels
    #d = np.genfromtxt('./20180116_RPS_monitor_2.csv',delimiter=',', skip_header=1)
    d = np.genfromtxt(filenamex,delimiter=',',names=True)
    fig.clf()
    dnames = d.dtype.names
    t = dnames[0]
    tn = d[t]
    plen = len(dnames)-2
    for i in range(1,plen+1):
      dn = d[dnames[i]]
      plt.subplot(plen, 1, i)

      if Ntail == 0:
        plt.plot(tn, dn)

      else:
        plt.plot(tn[-Ntail:], dn[-Ntail:])

      plt.title(dnames[i])
      plt.grid()


    plt.xlabel('Time (s)')
    plt.subplots_adjust(hspace=1.2)
    plt.show(block=False)

    print("hit 'enter' to refresh or integer N for last N points")
    time.sleep(1)
    input_string = raw_input()

    if len(input_string) == 0:
      Ntail = 0
    else:
      try:
        Ntail = int(input_string)
      except KeyboardInterrupt:
        exit()
    print "Loading the last {0} points...".format(Ntail)
