import argparse
from builtins import input
import time
import string
import atexit
import threading
import logging
from bitalino import BITalino, ExceptionCode
from yapsy.PluginManager import PluginManager
# from pyqtgraph.Qt import QtGui, QtCore


BITALINO_LOCK = threading.Lock()

class BitalinoController(BITalino):
    def __init__(self, macAddress, timeout=None):
        super(BitalinoController, self).__init__(macAddress, timeout)
        self.samples = []

    def start_streaming(self, callbacks_list, sampling_rate, acq_channels, nb_samples):
        self.start(sampling_rate, acq_channels)
        while self.started:
            try:
                with BITALINO_LOCK:
                    samples = self.read(nb_samples)
            except Exception as e:
                exception_message = str(e)
                # This exception may occur during the abrupt ending of communications, ignore them
                if exception_message == ExceptionCode.DEVICE_NOT_IN_ACQUISITION:
                    return
                else:
                    raise
            self.samples.append(samples)
            for call in callbacks_list:
                call(samples)

    def init(self, callbacks_list, samplingRate, acq_channels, nb_samples):
        user_input = ''
        while (user_input != "/exit"):
            if user_input == '':
                pass
            elif self.started and user_input != "/stop":
                print("Error: the board is streaming data, use '/stop' before running other commands")
            else:
                # TODO: extend with other commands
                if ("/start" == user_input):
                    # start streaming in a new thread
                    boardThread = threading.Thread(target=self.start_streaming,
                                                   args=(callbacks_list, samplingRate, acq_channels, nb_samples),
                                                   name='worker')
                    boardThread.daemon = True
                    try:
                        # TODO: ensure that self.started is thread-safe
                        boardThread.start()
                        print('Starting streaming')
                    except:
                        raise
                elif ('/stop' == user_input):
                    with BITALINO_LOCK:
                        self.stop()
                        print('Stopping streaming')
                else:
                    print("Error: Unrecognized command")
            user_input = input('$ ')


def parse_args(manager):
    parser = argparse.ArgumentParser(description="Bitalino controller")
    parser.add_argument('-l', '--list', action='store_true',
                        help="List available plugins")
    parser.add_argument('-i', '--info', metavar='PLUGIN',
                        help="Show more information about a plugin")
    parser.add_argument('--log', dest='log', default=False, action='store_true',
                        help="Do logging?")
    parser.add_argument('-m', '--mac',
                        help="MAC address of the Bitalino (e.g., 20:16:02:26:61:54)")
    parser.add_argument('-c', '--channels', metavar='CHANNELS', default='100000',
                        help="Vector of 0s and 1s specifying which channels should be activated" +
                             "(e.g.: 100010 would activate channels 1 and 5)")
    parser.add_argument('-s', '--sampling', type=int, default=1000,
                        help="Sampling rate in Hz")
    parser.add_argument('-n', '--nSamples', type=int, default=100,
                        help="Number of samples to be read in each call to Bitalino")
    # Plugins argument: plugin name +  parameters for the plugin
    parser.add_argument('-p', '--plugin', metavar=('PLUGIN', 'PARAMS'),
                        action='append', nargs='+',
                        help="Activate plugins and set its parameters")
    # parser.set_defaults(log=False)
    args = parser.parse_args()
    # Take required actions
    if not (args.mac or args.list or args.info):
        parser.error(
            'No action requested. Use `--mac MAC_ADDRESS` to connect to Bitalino; '
            '`--list` to show available plugins or `--info [plugin_name]` to get more information.')

    if args.list:
        print("Available plugins:")
        for plugin in manager.getAllPlugins():
            print('\t{}'.format(plugin.name))
        exit()

    if args.info:
        plugin = manager.getPluginByName(args.info)
        if plugin == None:
            print("Error: Plugin [{0}] not found or failed during load".format(args.info))
        else:
            print(plugin.description)
            plugin.plugin_object.show_help()
        exit()

    if args.log:
        print("Logging Enabled: " + str(args.log))
        logging.basicConfig(filename="Bitalino.log", format='%(asctime)s - %(levelname)s : %(message)s',
                            level=logging.DEBUG)
        logging.getLogger('yapsy').setLevel(logging.DEBUG)
        logging.info('---------LOG START-------------')
        logging.info(args)

    activated_channels = [i for i, ltr in enumerate(args.channels) if ltr == '1']
    deactivated_channels = [i for i, ltr in enumerate(args.channels) if ltr == '0']
    # check if the format of args.channel was correct by checking that activated_channels UNION deactivated_channels
    # equals [0, 1, 2, ..., 5]
    if len(set(range(6)) ^ set(activated_channels).union(set(deactivated_channels))) != 0:
        parser.error('Invalid --channels argument')

    plugin_list, callbacks_list = activate_plugins(args, manager, args.sampling, activated_channels, args.nSamples)

    return args.mac, args.sampling, args.nSamples, activated_channels, plugin_list, callbacks_list


def activate_plugins(args, manager, sampling_rate, acq_channels, nb_samples):
    plugin_list = []
    callbacks_list = []
    if args.plugin:
        for plugin_description in args.plugin:
            plugin_name = plugin_description[0]
            plugin_args = plugin_description[1:]
            plugin = manager.getPluginByName(plugin_name)
            if plugin == None:
                print("Error: Plugin [{0}] not found or failed during load".format(plugin_name))
            else:
                if not plugin.plugin_object.activate_plugin(plugin_args, sampling_rate, acq_channels, nb_samples):
                    print("Error while activating [{0}]".format(plugin_name))
                else:
                    plugin_list.append(plugin.plugin_object)
                    callbacks_list.append(plugin.plugin_object)

    if len(plugin_list) == 0:
        print("WARNING: no plugins selected")
    return plugin_list, callbacks_list

def deactivate_plugins(plugins_list):
    for plugin in plugins_list: 
        plugin.deactivate_plugin()


if __name__ == '__main__':
    # Load plugins from the plugins directory
    manager = PluginManager()
    manager.setPluginPlaces(["plugins"])
    manager.collectPlugins()

    (macAddress, sampling_rate, nb_samples, acq_channels,
     plugin_list, callbacks_list) = parse_args(manager)

    # app = QtGui.QApplication([])
    # app.processEvents()

    # Connect to BITalino
    device = BitalinoController(macAddress)
    # Configure the device
    device.init(callbacks_list, sampling_rate, acq_channels, nb_samples)
    try:
        deactivate_plugins(callbacks_list)
    finally: 
        device.close()

    print("The end")
