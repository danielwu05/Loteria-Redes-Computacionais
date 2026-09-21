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
        self.is_running = False

    def start(self):
        try:
            self.s.bind((self.host, self.port))
            self.s.listen()
            self.is_running = True
            print("server online!")
        except Exception as e:
            print(f"Erro ao inicializar o servidor: {e}")
            raise e

    def client_worker(self, conn_socket, addr):
        print(f"worker started for client: {addr}")

        client_state = {
            "lottery": Lottery(),
            "bets": [],
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
        except Exception as e:
            print(f"Erro inesperado no worker do cliente {addr}: {e}")

        finally:
            client_state["running"] = False
            self.remove_client(conn_socket)

    def accept_clients(self):
        while self.is_running:
            try:
                conn_socket, addr = self.s.accept()
            except (OSError, socket.error):
                if not self.is_running:
                    break
                continue

            with self.clients_lock:
                if len(self.clients) >= self.max_clients:
                    server_full = True

                else:
                    self.clients.append(conn_socket)
                    server_full = False
                    clients_connected = len(self.clients)

            if server_full:
                message = "Server full! Maximum number of clients reached."
                try:
                    conn_socket.send(message.encode("utf-8"))
                except OSError:
                    pass
                finally:
                    try:
                        conn_socket.close()
                    except OSError:
                        pass

                print(f"connection refused: {addr}")

                continue

            try:
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
            except (OSError, socket.error) as e:
                print(f"Erro ao inicializar conexão com cliente {addr}: {e}")
                self.remove_client(conn_socket)

    def remove_client(self, conn_socket):

        with self.clients_lock:
            if conn_socket in self.clients:
                self.clients.remove(conn_socket)

            clients_connected = len(self.clients)
            self.client_threads = [t for t in self.client_threads if t.is_alive()]
        try:
            conn_socket.close()
        except OSError:
            pass

        try:
            conn_socket.close()
        except OSError:
            pass

        print(
            f"client removed. clients connected: {clients_connected}/{self.max_clients}"
        )

    def is_int_guess(self, items):
        if not items:
            return False
        for item in items:
            try:
                int(item)
            except ValueError:
                return False
        return True

    def process_input(self, conn_socket, client_state):

        lot = client_state["lottery"]
        while client_state["running"]:
            try:
                lot_info = lot.get_params()
                send = f"\n\n\n\nconfigurações da loteria\n\ninicio: {lot_info[0]}\nfim: {lot_info[1]}\nquantidade: {lot_info[2]}"
                conn_socket.send(send.encode("utf-8"))

                bytesReceived = conn_socket.recv(1024)
                if not bytesReceived:
                    print("client disconnected")
                    client_state["running"] = False
                    break
                else:
                    message = bytesReceived.decode("utf-8")
                    input = message.lstrip().split(" ")
                    try:
                        if len(input) == 2 and input[0][0] == ":":
                            try:
                                val = int(input[1])
                            except ValueError:
                                raise ValueError("O valor deve ser um número inteiro")

                            with client_state["lock"]:
                                if input[0] == ":inicio":
                                    lot.setting_initial(val)
                                elif input[0] == ":fim":
                                    lot.setting_final(val)
                                elif input[0] == ":qtd":
                                    lot.setting_count(val)
                                else:
                                    print("invalid command")
                        elif self.is_int_guess(input):
                            with client_state["lock"]:
                                client_guess = [int(char) for char in input]
                                if any(n < 0 for n in client_guess):
                                    raise ValueError(
                                        "A aposta não pode conter números negativos"
                                    )
                                client_state["bets"] = client_guess

                        else:
                            raise ValueError(
                                "Uso: :inicio <NUMERO>, :fim <NUMERO> ou :qtd <NUMERO>"
                            )

                    except ValueError as e:
                        error_message = f"Error: {str(e)}"
                        try:
                            conn_socket.send(error_message.encode("utf-8"))
                        except OSError:
                            client_state["running"] = False
            except (
                ConnectionResetError,
                ConnectionAbortedError,
                BrokenPipeError,
                OSError,
            ) as e:
                print(f"socket error or client disconnected abruptly: {e}")
                client_state["running"] = False
                break
            except Exception as e:
                print(f"unexpected error processing input: {e}")
                client_state["running"] = False
                break

    def send_results(self, conn_socket, client_state):
        while client_state["running"]:
            try:
                for _ in range(60):
                    if not client_state["running"]:
                        return
                    time.sleep(1)

                lot = client_state["lottery"]
                if not client_state["running"]:
                    break

                result_array = lot.sorting_numbers()

                with client_state["lock"]:
                    message = ""
                    if client_state["bets"]:
                        try:
                            lot.validating_numbers(client_state["bets"])
                            correct = lot.checking_numbers(
                                client_state["bets"], result_array
                            )

                            if result_array:
                                message = f"user guess: {sorted(client_state['bets'])}\n casino results: {sorted(result_array)}\n correct numbers: {sorted(correct)}"

                        except ValueError as ve:
                            error_message = f"Invalid Bet Error: {str(ve)}\n"
                            conn_socket.send(error_message.encode("utf-8"))

                        client_state["bets"].clear()

                    else:
                        message = (
                            f"no user guess\n casino results: {sorted(result_array)}"
                        )

                    conn_socket.send(message.encode("utf-8"))

            except (
                ConnectionResetError,
                ConnectionAbortedError,
                BrokenPipeError,
                OSError,
            ):
                client_state["running"] = False
                break
            except Exception as e:
                print(f"unexpected error sending results: {e}")
                client_state["running"] = False
                break

    def close_server(self):
        self.is_running = False
        with self.clients_lock:
            for conn_socket in self.clients:
                try:
                    conn_socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                try:
                    conn_socket.close()
                except OSError:
                    pass

            self.clients.clear()

        try:
            self.s.close()
        except OSError:
            pass
