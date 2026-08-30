from serverObj import Server
import threading
import sys


def main():

    host = "localhost"
    port = 9090

    if len(sys.argv) != 2:
        print("Usage: python server.py <max_clients>")
        sys.exit(1)

    max_clients = int(sys.argv[1])

    s = Server(
        host,
        port,
        max_clients
    )

    s.start()

    try:
        s.accept_clients()

    except KeyboardInterrupt:
        print("\nshutting down server")

    finally:
        s.close_server()


if __name__ == "__main__":
    main()
