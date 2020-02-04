# Bitalino controller in Python

A **Python** project designed to control a [BITalino](http://bitalino.com/en/community/projects) board by means of Plugins (inspired by the [OpenBCI library](https://github.com/OpenBCI/OpenBCI_Python)). This repository is intended to provide
a "bare-bones" BITalino controller, which should be improved as part of a undergraduate course on biosignals. Therefore, it is unlikely that new features will be added in the future. However, if you are interested in further develop the project, 
don't hesitate in forking it (see [License](#license)).

## Installation
This project is implemented in **Python** and should work for both Python 2.7 and 3.X. The code has been tested in both Linux and Windows operating systems. It should also work out of the box in MacOS-based systems (untested).

The project depends on the packages listed in *requirements.txt*. At the same time, some of these packages have some system-dependencies that should be met before trying to install them:

* In MacOS: you don't need to install any system-dependency.
* In Debian/Ubuntu-based distributions: 
```bash
$ sudo apt install python-xlib libbluetooth-dev
$ pip install PyBluez
```
* In Windows: please follow this guide about [preparing PyBluez on Windows 10](https://github.com/BITalinoWorld/revolution-python-api#prepare-pybluez-installation-on-windows-10)

Once you have completed the previous steps, you may install the python dependencies using the following pip command:
```bash
$ pip install -r requirements.txt
```

Once all the dependencies are satisfied, it is enough to download the project sources and run the proper python script.

## Basic usage
Before using the Python scripts the BITalino board should be Bluetooth-paired with your computer (Bluetooth code is 1234).

```BitalinoController.py``` provides a simple user interface to manage plugins and communicate with the BITalino board. Several command line arguments can be used to configure the board. For a complete list, consult
```bash
python BitalinoController.py --help
```
For a basic usage, only the MAC address of the BITalino board is required:
```bash
$ python BitalinoController.py -m 20:16:02:26:61:54
```
The program should stablish a Bluetooth connection with the board and open a simple terminal (indicated with a ```$``` symbol). Available commands are:
* ```\start```: starts the streaming of data.
* ```\stop```: stops the streaming.
* ```\exit```: ends the script.

### Plugins
#### Use of plugins
Plugins are based on the [Yapsy](http://yapsy.sourceforge.net/) plugin system. To obtain a list of the available plugins, the following command can be used:

```bash
python BitalinoController.py -l
```

Art the moment, only two plugins are available. A print plugin and a TCP-streaming plugin. Please note that, as part of the course, the TCP-streaming plugin is severely limited, and it only streams the last active channel.

The Yapsy plugin systems looks for available plugins under the ```plugins``` folder. To use a plugin just use its name after the ```-p``` argument. Additional arguments
for the plugin should be specified after its name. For example, to print samples and stream the last active channel through TCP to the local 6666 port:

```bash
python BitalinoController.py -p stream 127.0.0.1 6666 -p print
```

#### Create new plugins
To create a new plugin, a new class extending ```IPluginBitalino``` should be created. For a minimal example, see [plugins/PluginPrint.py](plugin/PluginPrint.py). Finally, describe your plugin with a ```[name-of-class].yapsy-plugin``` (see [plugins/PluginPrint.yapsy-plugin](plugins/PluginPrint.yapsy-plugin)).

### A basic visualization tool
When using the ```BitalinoController``` with the default parameters of the ```PluginStream```, a basic signal visualizer can be used if the *optional-requirements.txt* file has been installed:
```bash
$ pip install -r optional-requirements.txt # installs additional optional dependencies
```
The following command starts a client listening at localhost:6666 which plots the channel streamed by ```PluginStream```:
```bash
$ python BitalinoGUI.py 
```

## License

This project is licensed under the terms of the [GPL v3 license](LICENSE).
