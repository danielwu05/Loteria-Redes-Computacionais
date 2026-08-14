#include <arpa/inet.h>
#include <cstring>
#include <ctime>
#include <iomanip>
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
      cout << "Client has disconnected from the server" << endl;
      break;

    } else {
      buffer[bytesReceived] = '\0';

      cout << "Message from client: " << buffer << endl;
    }
  }
}

void input(int clientSocket) {
  while (true) {

    string input;
    getline(cin, input);
    const char *message = input.c_str();

    if (send(clientSocket, message, strlen(message), 0) == -1) {
      perror("send");
      close(clientSocket);
      break;
    }

    cout << "Message sent!" << endl;
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

  cout << "Connected to server!" << endl;

  thread t1(input, clientSocket);
  thread t2(listen_server, clientSocket);

  t1.join();
  t2.join();

  close(clientSocket);

  return 0;
}
