from clientObj import Client

host = "localhost"
port = 8080


def main():
    c = Client(host, port)
    c.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
