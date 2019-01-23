from yapsy.IPlugin import IPlugin

class IPluginBitalino(IPlugin):
    """
    Defines the basic interface for a Bitalino plugin. When creating a specific plugin you should
    override:
        - activate/deactivate: called at plugin activation/deactivation.
        - __call__: handles streamed samples from Bitalino.
        - show_help: shows plugin's help.
    Note that the activate_plugin and deactivate_plugin methods should not be overrided.
    """
    def activate_plugin(self, args, sampling_rate, acq_channels, nb_samples):
        """
        :param args: arguments from command line
        :param sampling_rate: Bitalino sampling rate in  Hzs
        :param acq_channels: Channels to be adquired by Bitalino
        :param nb_samples: Number of samples read in each call to Bitalino
        :return: Boolean value indicating if the plugin is activated
        """
        self.args = args
        self.sampling_rate = sampling_rate
        self.acq_channels = acq_channels
        self.nb_acq_channels = len(acq_channels)
        self.nb_samples = nb_samples
        self.activate()
        self.is_activated = True
        return self.is_activated

    # Specific Plugin logic goes here
    def activate(self):
        print("Plugin {0} activated".format(self.__class__.__name__))

    # Alias for consistency with activate
    def deactivate_plugin(self):
        self.deactivate()

    # Specific Plugin logic goes here
    def deactivate(self):
        print("Plugin {0} deactivated".format(self.__class__.__name__))

    def show_help(self):
        print("Plugin {0} does not need any parameter".format(self.__class__.__name__))

    def __call__(self, samples):
        pass
