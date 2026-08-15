#include <arpa/inet.h>
#include <iostream>
#include <netinet/in.h>
#include <string>
#include <sys/socket.h>
#include <thread>
#include <unistd.h>

using namespace std;

void listen_server(int clientSocket) {
  while (true) {

    char buffer[1024] = {0};

    ssize_t bytesReceived = recv(clientSocket, buffer, sizeof(buffer) - 1, 0);

    if (bytesReceived == -1) {
      perror("recv");
    } else if (bytesReceived == 0) {
      cout << "Servidor desconectou" << endl;
      break;

    } else {
      buffer[bytesReceived] = '\0';

      cout << buffer;
    }
  }
}

void input(int clientSocket) {
  while (true) {

    string input;
    if (!getline(cin, input)) {
      shutdown(clientSocket, SHUT_WR);
      break;
    }

    string message = input + "\n";

    if (send(clientSocket, message.c_str(), message.size(), 0) == -1) {
      perror("send");
      close(clientSocket);
      break;
    }
  }
}
int main() {
  int clientSocket = socket(AF_INET, SOCK_STREAM, 0);

  if (clientSocket == -1) {
    perror("socket");
    return 1;
  }

  sockaddr_in serverAddress{};
  serverAddress.sin_family = AF_INET;
  serverAddress.sin_port = htons(9090);

  inet_pton(AF_INET, "127.0.0.1", &serverAddress.sin_addr);

  if (connect(clientSocket, (struct sockaddr *)&serverAddress,
              sizeof(serverAddress)) == -1) {
    perror("connect");
    close(clientSocket);
    return 1;
  }

  cout << "Conectado ao servidor. Digite os comandos ou apostas." << endl;

  thread t1(input, clientSocket);
  thread t2(listen_server, clientSocket);

  t1.join();
  t2.join();

  close(clientSocket);

  return 0;
}
