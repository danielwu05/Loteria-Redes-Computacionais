import socket
import string
from datetime import datetime


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.switch = [False, False, False, False]

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        self.s.bind((self.host, self.port))
        self.s.listen()

        (self.conn_socket, addr) = self.s.accept()
        current_time = datetime.now().strftime("%H:%M")
        time_connected = f"{current_time} - CONECTADO!!"
        self.conn_socket.send(time_connected.encode("utf-8"))

    def process_input(self):
        while True:
            try:
                bytesReceived = self.conn_socket.recv(1024)
                if not bytesReceived:
                    print("client disconnected")
                    break
                else:
                    message = bytesReceived.decode("utf-8")
                    input = message.split(" ")
                    if (
                        input[0][0] == ":"
                        and input[0][1].isnumeric()
                        and len(input[0]) == 2
                    ):
                        if input[0] == ":inicio":
                            self.switch[0] = True
                        elif input[0] == ":fim":
                            self.switch[1] = True
                        elif input[0] == ":qtd":
                            self.switch[2] = True
                        else:
                            print("invalid command")
                    elif all(item.isnumeric() for item in input):
                        self.switch[3] = True
                        self.client_guess = input
                    else:
                        print("input invalid")
            except KeyboardInterrupt:
                break

    def send_results(self):
        while True:
            try:
                if all(self.switch):
                    print("lottery complete")
                    self.switch[:] = [False] * len(self.switch)
                    message = f"user guess: {self.client_guess} \n casino results: {self.client_guess}"
                    self.conn_socket.send(message.encode("utf-8"))
            except KeyboardInterrupt:
                break

    def close_server(self):
        self.conn_socket.close()
        self.s.close()
