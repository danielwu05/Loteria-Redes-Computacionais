#include <condition_variable>
#include <cstring>
#include <ctime>
#include <format>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <netinet/in.h>
#include <queue>
#include <sstream>
#include <string>
#include <sys/socket.h>
#include <sys/types.h>
#include <thread>
#include <unistd.h>
#include <random>

using namespace std;

struct Comando {
  string cmd;
  int value;
};

int inicio, fim, qtd;

mutex mtx;
condition_variable cv;
queue<Comando> fila;

void process_input(int clientSocket) {
  while (true) {

    unique_lock<mutex> lck(mtx);
    cv.wait(lck, [] { return !fila.empty(); });

    Comando cmd = fila.front();

    fila.pop();

    if (cmd.cmd == ":inicio")
      inicio = cmd.value;
    if (cmd.cmd == ":fim")
      fim = cmd.value;
    if (cmd.cmd == ":qtd")
      qtd = cmd.value;

    lck.unlock();
    string val =
        format("received {} instruction and {} value", cmd.cmd, cmd.value);

    const char *message = val.c_str();

    ssize_t bytesSent = send(clientSocket, message, val.size(), 0);
  }
}

void receive_input(int clientSocket) {
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

      stringstream ss(buffer);

      string instruction;
      string value;

      if (ss >> instruction && ss >> value) {
        Comando new_cmd;
        if (instruction == ":inicio" || instruction == ":fim" ||
            instruction == ":qtd") {
          new_cmd.cmd = instruction;
          new_cmd.value = stoi(value);
          {
            lock_guard<mutex> lck(mtx);
            fila.push(new_cmd);
          }
          cv.notify_one();
        } else {
          cout << "Unkown instruction" << endl;
        }
      }
    }
  }
}

int main() {
  int serverSocket = socket(AF_INET, SOCK_STREAM, 0);

  if (serverSocket == -1) {
    perror("socket");
    return 1;
  }

  sockaddr_in serverAddress{};
  serverAddress.sin_family = AF_INET;
  serverAddress.sin_port = htons(9090);
  serverAddress.sin_addr.s_addr = INADDR_ANY;

  if (bind(serverSocket, (struct sockaddr *)&serverAddress,
           sizeof(serverAddress)) == -1) {
    perror("bind");
    close(serverSocket);
    return 1;
  }

  if (listen(serverSocket, 5) == -1) {
    perror("listen");
    close(serverSocket);
    return 1;
  }

  cout << "Server waiting on port 9090..." << endl;

  int clientSocket = accept(serverSocket, nullptr, nullptr);

  if (clientSocket == -1) {
    perror("accept");
    close(serverSocket);
    return 1;
  }

  time_t now = time(nullptr);

  tm *time_now = localtime(&now);

  cout << put_time(time_now, "%H:%M") << " - Client connected!" << endl;

  thread t1(receive_input, clientSocket);
  thread t2(process_input, clientSocket);

  t1.join();
  t2.join();


  close(clientSocket);
  close(serverSocket);

  return 0;
}
