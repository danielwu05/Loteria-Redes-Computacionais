import socket
import threading
from datetime import datetime
import time
from lottery import Lottery


class Server:
    def __init__(self, host, port, max_clients):
        
        self.host = host
        self.port = port
        self.max_clients = max_clients

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.clients = []
        self.clients_lock = threading.Lock()
        self.client_threads = []
        self.client_guess = []
        self.correct = []
        self.result_array = []
        
    def start(self):
        self.s.bind((self.host, self.port))
        self.s.listen()

        print("server online!")

    def client_worker(self, conn_socket, addr):
     print(f"worker started for client: {addr}")
     try:
        receive_thread = threading.Thread(
            target=self.process_input,
            args=(conn_socket,)
        )

        result_thread = threading.Thread(
            target=self.send_results,
            args=(conn_socket,)
        )

        receive_thread.start()
        result_thread.start()

        receive_thread.join()
        result_thread.join()

     finally:
        self.remove_client(conn_socket)
        


    def accept_clients(self):
     while True:
        conn_socket, addr = self.s.accept()

        with self.clients_lock:

            if len(self.clients) >= self.max_clients:
                server_full = True

            else:
                self.clients.append(conn_socket)
                server_full = False
                clients_connected = len(self.clients)

        if server_full:
            message = "Server full! Maximum number of clients reached."

            conn_socket.send(
                message.encode("utf-8")
            )

            conn_socket.close()

            print(f"connection refused: {addr}")

            continue

        current_time = datetime.now().strftime("%H:%M")
        time_connected = f"{current_time} - CONECTADO!!"

        conn_socket.send(
            time_connected.encode("utf-8")
        )

        print(f"client connected: {addr}")
        print(
            f"clients connected: "
            f"{clients_connected}/{self.max_clients}"
        )

        worker = threading.Thread(
            target=self.client_worker,
            args=(conn_socket, addr)
        )
        self.client_threads.append(worker)
        worker.start()

    def remove_client(self, conn_socket):

     with self.clients_lock:

         if conn_socket in self.clients:
            self.clients.remove(conn_socket)

         clients_connected = len(self.clients)

     conn_socket.close()

     print(
        f"client removed. "
        f"clients connected: {clients_connected}"
     )

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
                    input = message.lstrip().split(" ")
                    if len(input) == 2 and input[0][0] == ":" and input[1].isnumeric():
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
                        try:
                            lot.validating_numbers(self.client_guess)
                            self.result_array = lot.sorting_numbers()
                            self.correct = lot.checking_numbers(
                                self.client_guess, self.result_array
                            )
                        except ValueError as e:
                            error_message = f"Error: {str(e)}"
                            self.conn_socket.send(error_message.encode("utf-8"))
            except OSError as e:
                print(f"socket error: {e}")
                break
    def send_results(self):
        while True:
            try:
                time.sleep(10)
                message = f"\n user guess: {sorted(self.client_guess)} \n casino results: {sorted(self.result_array)} \n correct numbers: {sorted(self.correct)}"
                if self.client_guess:
                    self.conn_socket.send(message.encode("utf-8"))
                    self.client_guess.clear()
                    self.correct.clear()
                    self.result_array.clear()

            except KeyboardInterrupt:
                break

def close_server(self):

    with self.clients_lock:

        for conn_socket in self.clients:

            try:
                conn_socket.close()

            except OSError:
                pass

        self.clients.clear()

    self.s.close()
