from serverObj import Server
import sys


def main():

    host = "localhost"
    port = 9090

    if len(sys.argv) != 2:
        print("Usage: python server.py <max_clients>")
        sys.exit(1)

    try:
        max_clients = int(sys.argv[1])
        if max_clients <= 0:
            raise ValueError
    except ValueError:
        print("Erro: O número máximo de clientes deve ser um inteiro positivo.")
        sys.exit(1)
    

    s = Server(host, port, max_clients)

    try:
        s.start()
        s.accept_clients()

    except (KeyboardInterrupt, SystemExit):
        print("\nshutting down server")
    except Exception as e:
        print(f"Erro inesperado no servidor: {e}")
    finally:
        s.close_server()


if __name__ == "__main__":
    main()
