#include <iostream>
#include <cstring>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

using namespace std;

int main()
{
    int clientSocket = socket(AF_INET, SOCK_STREAM, 0);

    if (clientSocket == -1) {
        perror("socket");
        return 1;
    }

    sockaddr_in serverAddress{};
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_port = htons(9090);

    inet_pton(AF_INET, "127.0.0.1", &serverAddress.sin_addr);

    if (connect(clientSocket,
                (struct sockaddr*)&serverAddress,
                sizeof(serverAddress)) == -1)
    {
        perror("connect");
        close(clientSocket);
        return 1;
    }

    cout << "Connected to server!" << endl;

    const char* message = "Hello, server!";

    if (send(clientSocket,
             message,
             strlen(message),
             0) == -1)
    {
        perror("send");
        close(clientSocket);
        return 1;
    }

    cout << "Message sent!" << endl;

    close(clientSocket);

    return 0;
}