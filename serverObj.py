import socket
from datetime import datetime
import time
from lottery import Lottery


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        self.s.bind((self.host, self.port))
        self.s.listen()

        (self.conn_socket, addr) = self.s.accept()
        current_time = datetime.now().strftime("%H:%M")
        time_connected = f"{current_time} - CONECTADO!!"
        self.conn_socket.send(time_connected.encode("utf-8"))

        print(f"server online! addr: {addr} ")

    def process_input(self):
        lot = Lottery()
        while True:
            try:
                bytesReceived = self.conn_socket.recv(1024)
                if not bytesReceived:
                    print("client disconnected")
                    break
                else:
                    message = bytesReceived.decode("utf-8")
                    input = message.split(" ")
                    if input[0][0] == ":" and input[1].isnumeric() and len(input) == 2:
                        if input[0] == ":inicio":
                            print("inicio")
                            lot.setting_initial(int(input[1]))
                        elif input[0] == ":fim":
                            print("fim")
                            lot.setting_final(int(input[1]))
                        elif input[0] == ":qtd":
                            print("qtd")
                            lot.setting_count(int(input[1]))
                        else:
                            print("invalid command")
                    elif all(item.isnumeric() for item in input):
                        self.client_guess = [int(char) for char in input]
                        self.result_array = lot.sorting_numbers()
                        self.correct = lot.checking_numbers(
                            self.client_guess, self.result_array
                        )
                    else:
                        print("input invalid")
            except KeyboardInterrupt:
                break

    def send_results(self):
        while True:
            try:
                time.sleep(60)
                print("lottery complete")
                message = f"\n user guess: {self.client_guess} \n casino results: {self.result_array} \n correct numbers: {self.correct}"
                self.conn_socket.send(message.encode("utf-8"))
                self.client_guess.clear()
                self.correct.clear()
                self.result_array.clear()

            except KeyboardInterrupt:
                break

    def close_server(self):
        self.conn_socket.close()
        self.s.close()
