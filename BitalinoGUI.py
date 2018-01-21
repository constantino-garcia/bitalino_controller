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
        print('connecting to {} port {}'.format(*server_address))
        self.sock.connect(server_address)
        self.infile = self.sock.makefile()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.__update)
        self.timer.start(0)

    def __del__(self):
        try:
            print('Clossing the connection')
            self.sock.close()
            self.infile.close()
        except Exception:
            print "Error while closing the connection"

    def __update(self):
        try:
            data = self.infile.readline()
            if data:
                data = json.loads(data)
                samples = data['samples']
                self.channel_data += list(samples)
                self.curve.setData(self.channel_data)
        except Exception as e:
            print(e)

if __name__ == '__main__':
   import sys
   app = QtGui.QApplication([])
   gui=BitalinoGUI()
   gui.resize(800, 800)
   gui.setWindowTitle('Bitalino GUI')
   gui.show()
   app.processEvents()
   sys.exit(app.exec_())
