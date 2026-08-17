import socket
import threading
import sys

def listen_server(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            
            if not data:
                print("\nServidor desconectou")
                break

            print(data.decode("utf-8", errors="replace"), end="")
            
        except Exception as e:
            break

def input_handler(client_socket):
    while True:
        try:
            user_input = sys.stdin.readline()
            
            if not user_input:
                client_socket.shutdown(socket.SHUT_WR)
                break
        
            client_socket.sendall(user_input.encode("utf-8"))
            
        except Exception as e:
            client_socket.close()
            break


def main():

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    host = "127.0.0.1"
    port = 9090

    try:
        client_socket.connect((host, port))
    except Exception as e:
        print(f"Erro ao conectar na árvore central: {e}")
        return

    print("Conectado ao servidor. Digite os comandos ou apostas.")

 
    t1 = threading.Thread(target=input_handler, args=(client_socket,))
    t2 = threading.Thread(target=listen_server, args=(client_socket,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    client_socket.close()


if __name__ == "__main__":
    main()