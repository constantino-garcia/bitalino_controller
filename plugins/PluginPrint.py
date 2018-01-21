import IPluginBitalino

class PluginPrint(IPluginBitalino.IPluginBitalino):
    def activate_plugin(self, args, sampling_rate, acq_channels, nb_samples):
        self.formatting_string = "{:2.0f} " * 5 + "{:8.3f} " * len(acq_channels)
        return super(PluginPrint, self).activate_plugin(args, sampling_rate, acq_channels, nb_samples)

    def activate(self):
        print("Print activated")

    # called with each set of samples received from Bitalino
    def __call__(self, samples):
        for sample in samples:
            print(self.formatting_string.format(*sample))

