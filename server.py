import socket
from datetime import datetime


def process_input(conn_socket):
    while True:
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
                if input[0] == ":fim":
                    print("its fim")
                if input[0] == ":qtd":
                    print("its qtd")
                else:
                    print("invalid cmd")
            else:
                print("its a guess")
                print(f"guess vector: {input}")


def send_results(conn_socket):
    while True:
        pass


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

process_input(conn_socket)
