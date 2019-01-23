# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtGui, QtCore
from collections import deque
import socket
import pyqtgraph as pg
import threading
import json

class BitalinoGUI(QtGui.QMainWindow):
    """
    Simple Graphical interface plotting a single channel from the Bitalino device
    """
    def __init__(self, server_address=('localhost', 6666), npoints=5000):
        self.channel_data = deque([], npoints)
        QtGui.QMainWindow.__init__(self)
        view = pg.GraphicsLayoutWidget()
        self.setCentralWidget(view)
        pl = view.addPlot(title="Bitalino Data")
        self.curve = pl.plot(self.channel_data)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('connecting to {} port {} ...'.format(*server_address))
        self.sock.connect(server_address)
        print('connected')

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.__update)
        self.timer.start(0)

    def __del__(self):
        try:
            print('Clossing the connection')
            self.sock.close()
        except Exception:
            print("Error while closing the connection")

    def __update(self, MAX_BUFFER_SIZE=4096):
        try:
            data = self.sock.recv(MAX_BUFFER_SIZE)
            # MAX_BUFFER_SIZE is how big the message can be
            # this is test if it's sufficiently big
            import sys
            siz = sys.getsizeof(data)
            if  siz >= MAX_BUFFER_SIZE:
                print("The length of input is probably too long: {}".format(siz))
            if data:
                data = data.decode("utf8").rstrip()

                data = json.loads(data)
                samples = data['samples']
                self.channel_data += list(samples)
                self.curve.setData(self.channel_data)
        except Exception as e:
            print(e)

if __name__ == '__main__':
   import sys

   app = QtGui.QApplication([])

   if len(sys.argv) > 1:
        port = int(sys.argv[1])
        gui=BitalinoGUI(('localhost', port))
   else:
        gui=BitalinoGUI()
   gui.resize(800, 800)
   gui.setWindowTitle('Bitalino GUI')
   gui.show()

   app.processEvents()
   sys.exit(app.exec_())
