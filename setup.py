from distutils.core import setup

setup(
    name='LabJackDAQ',
    version='0.1dev',
    packages=['usbtmc',
              'time',
              'datetime',
              'serial',
              'numpy',
              'os',
              'argparse',
              'sys',
              'pandas',
              'pyqtgraph',
              'pyqt5==10',

              ],
    license='',
    long_description=open('README.txt').read(),
)
