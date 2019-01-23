import IPluginBitalino

class PluginPrint(IPluginBitalino.IPluginBitalino):
    def activate(self):
        self.formatting_string = "{:2.0f} " * 5 + "{:8.3f} " * len(self.acq_channels)
        print("Print activated")

    # called with each set of samples received from Bitalino
    def __call__(self, samples):
        for sample in samples:
            print(self.formatting_string.format(*sample))

