import socket
import threading
from datetime import datetime

switch = [False, False, False, False]

client_guess = []

placeholder_array = [1, 2, 3, 4, 5, 6]


def process_input(conn_socket):
    while True:
        try:
            bytesReceived = conn_socket.recv(4096)
            if not bytesReceived:
                print("client disconnected")
                break
            else:
                message = bytesReceived.decode("utf-8")
                input = message.split(" ")
                if input[0][0] == ":":
                    print("its a command")
                    if input[0] == ":inicio":
                        print("its inicio")
                        switch[0] = True
                    elif input[0] == ":fim":
                        print("its fim")
                        switch[1] = True
                    elif input[0] == ":qtd":
                        print("its qtd")
                        switch[2] = True
                    else:
                        print("invalid cmd")
                else:
                    print("its a guess")
                    switch[3] = True
                    client_guess = input
                    print(f"guess vector: {input}")
        except KeyboardInterrupt:
            break


def send_results(conn_socket):
    while True:
        try:
            if all(switch):
                print("lotery complete")
                switch[:] = [False] * len(switch)
                message = f"user guess: {placeholder_array} \n casino results: {placeholder_array}"
                conn_socket.send(message.encode("utf-8"))
        except KeyboardInterrupt:
            break


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = "localhost"
port = 8080

s.bind((host, port))
s.listen()

(conn_socket, addr) = s.accept()

current_time = datetime.now().strftime("%H:%M")

time_connected = f"{current_time} - CONECTADO!!"

conn_socket.send(time_connected.encode("utf-8"))

t1 = threading.Thread(target=process_input, args=(conn_socket,))
t2 = threading.Thread(target=send_results, args=(conn_socket,))

t1.start()
t2.start()

t1.join()
t2.join()

conn_socket.close()
s.close()
