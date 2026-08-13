#include <iostream>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <thread>

using namespace std;

int rvinput(int clientSocket){

    while (true){
 char buffer[1024] = {0};

    ssize_t bytesReceived =
        recv(clientSocket,
             buffer,
             sizeof(buffer) - 1,
             0);

    if (bytesReceived == -1) {
        perror("recv");
        return -1;
    }
    else {
        buffer[bytesReceived] = '\0';

        cout << "Message from client: "
             << buffer << endl;
    }
    }   

    return 0;
}




int main()
{

    int serverSocket = socket(AF_INET, SOCK_STREAM, 0);

    if (serverSocket == -1) {
        perror("socket");
        return 1;
    }

    sockaddr_in serverAddress{};
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_port = htons(9090);
    serverAddress.sin_addr.s_addr = INADDR_ANY;

    if (bind(serverSocket,
             (struct sockaddr*)&serverAddress,
             sizeof(serverAddress)) == -1)
    {
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

    int clientSocket =
        accept(serverSocket, nullptr, nullptr);

    if (clientSocket == -1) {
        perror("accept");
        close(serverSocket);
        return 1;
    }

    cout << "Client connected!" << endl;

    thread t1(rvinput, clientSocket);
    t1.join();

    close(clientSocket);
    close(serverSocket);

    return 0;
}