import socket
import queue
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

        self.responseQueue = queue.Queue()

        self.configs_prontas = [False, False, False]

    def start(self):
        self.s.bind((self.host, self.port))
        self.s.listen()

        print("server online!")

    def client_worker(self, conn_socket, addr):
        print(f"worker started for client: {addr}")

        client_state = {
            "lottery": Lottery(),
            "bets": [],
            "Flags": [False, False, False, False],
            "lock": threading.Lock(),
            "running": True,
        }
        try:
            receive_thread = threading.Thread(
                target=self.process_input, args=(conn_socket, client_state)
            )

            result_thread = threading.Thread(
                target=self.send_results, args=(conn_socket, client_state)
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

                conn_socket.send(message.encode("utf-8"))

                conn_socket.close()

                print(f"connection refused: {addr}")

                continue

            current_time = datetime.now().strftime("%H:%M")
            time_connected = f"{current_time} - CONECTADO!!"

            conn_socket.send(time_connected.encode("utf-8"))

            print(f"client connected: {addr}")
            print(f"clients connected: {clients_connected}/{self.max_clients}")

            worker = threading.Thread(
                target=self.client_worker, args=(conn_socket, addr)
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
            f"client removed. clients connected: {clients_connected}/{self.max_clients}"
        )

    def process_input(self, conn_socket, client_state):

        lot = client_state["lottery"]
        while client_state["running"]:
            try:
                lot_info = lot.get_params()
                send = f"lottery\nstart {lot_info[0]}\nend {lot_info[1]}\nquantity {lot_info[2]}"
                conn_socket.send(send.encode("utf-8"))

                bytesReceived = conn_socket.recv(1024)
                if not bytesReceived:
                    print("client disconnected")
                    client_state["running"] = False
                    self.remove_client(conn_socket)
                    break
                else:
                    message = bytesReceived.decode("utf-8")
                    input = message.lstrip().split(" ")
                    try:
                        if (
                            len(input) == 2
                            and input[0][0] == ":"
                            and input[1].isnumeric()
                        ):
                            with client_state["lock"]:
                                if input[0] == ":inicio":
                                    lot.setting_initial(int(input[1]))
                                    client_state["Flags"][0] = True
                                elif input[0] == ":fim":
                                    lot.setting_final(int(input[1]))
                                    client_state["Flags"][1] = True
                                elif input[0] == ":qtd":
                                    lot.setting_count(int(input[1]))
                                    client_state["Flags"][2] = True
                                else:
                                    print("invalid command")
                        elif all(item.isnumeric() for item in input):
                            with client_state["lock"]:
                                client_guess = [int(char) for char in input]
                                client_state["bets"] = client_guess
                                client_state["Flags"][3] = True

                    except ValueError as e:
                        error_message = f"Error: {str(e)}"
                        client_state["running"] = False
                        conn_socket.send(error_message.encode("utf-8"))
            except OSError as e:
                print(f"socket error: {e}")
                break

    def send_results(self, conn_socket, client_state):
        while client_state["running"]:
            lot = client_state["lottery"]
            try:
                for _ in range(60):
                    if not client_state["running"]:
                        return
                    time.sleep(1)

                    if all(client_state["Flags"]) or client_state["Flags"][3]:
                        break

                if not client_state["running"]:
                    break

                with client_state["lock"]:
                    lot.validating_numbers(client_state["bets"])
                    result_array = lot.sorting_numbers()
                    correct = lot.checking_numbers(client_state["bets"], result_array)

                    message = f"user guess: {sorted(client_state['bets'])} \n casino results: {sorted(result_array)} \n correct numbers: {sorted(correct)}"

                    conn_socket.send(message.encode("utf-8"))

            except KeyboardInterrupt:
                break

            finally:
                for i in range(4):
                    client_state["Flags"][i] = False

    def close_server(self):
        with self.clients_lock:
            for conn_socket in self.clients:
                try:
                    conn_socket.close()

                except OSError:
                    pass

            self.clients.clear()

        self.s.close()
