from threading import Thread
import socket, select, time
import IPluginBitalino
import pandas as pd


class MonitorNewConnections(Thread):
    """Monitor a TCP Stream to accept new connections"""
    def __init__(self, streamer):
        Thread.__init__(self)
        self.server = streamer

    def run(self):
        while True:
            self.server.check_connections()
            time.sleep(1)


class PluginStream(IPluginBitalino.IPluginBitalino):
    def __init__(self, ip='localhost', port=6666):
        self.ip = ip
        self.port = port
        # list of socket clients
        self.connections = []

    def activate(self):
        if len(self.args) > 0:
            self.ip = self.args[0]
        if len(self.args) > 1:
            self.port = int(self.args[1])

        print("Streaming through TCP to " + self.ip + ":" + str(self.port))
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(1)

        self.monitor = MonitorNewConnections(self)
        self.monitor.daemon = True
        self.monitor.start()

    def check_connections(self):
        # wait for incoming connections
        read_sockets, write_sockets, error_sockets = select.select([self.server_socket], [], [], 0)
        for sock in read_sockets:
            if sock is self.server_socket:
                conn, addr = self.server_socket.accept()
                self.connections.append(conn)
                print("Client ({}, {}) connected".format(*addr))

    def deactivate(self):
        for conn in self.connections:
            if conn != self.server_socket:
                conn.close()
        self.server_socket.close()

    def __call__(self, samples):
        failed_connections = []
        for conn in self.connections:
            try:
                # TODO: for the moment, just use the last channel
                data = pd.Series(pd.Series({'samples': samples[:, -1].flatten()})).to_json() + '\n'
                conn.send(data.encode("utf8"))
            except Exception as e:
                print("Failed " + str(conn))
                print(e)
                failed_connections.append(conn)
        for bad_conn in failed_connections:
            self.connections.remove(bad_conn)
            bad_conn.close()

    def show_help(self):
        print("""Optional arguments: [IP [port]]
			\t Default IP: 'localhost'
			\t Default port: 6666""")

