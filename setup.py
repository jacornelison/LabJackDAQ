from setuptools import setup

setup(
    name='LabJackDAQ',
    version='0.1dev',
    install_requires=['usbtmc',
              'time',
              'datetime',
              'serial',
              'numpy',
              'os',
              'argparse',
              'sys',
              'pandas',
              'pyqtgraph',
              'pyqt5==5.10',
              ],
    license='',
    long_description=open('README.txt').read(),
)

