from setuptools import setup

setup(
    name='LabJackDAQ',
    version='0.1dev',
    install_requires=['numpy',
              'python-usbtmc',
              'pyusb',
              'serial',
              'pandas',
              'pyqtgraph',
              'PyQt5==5.10',
              ],
    license='',
    long_description=open('README.md').read(),
)

