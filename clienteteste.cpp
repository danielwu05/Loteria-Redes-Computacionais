#include <iostream>
#include <cstring>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <ctime>
#include <iomanip>
#include <thread>
#include <string>



using namespace std;


void readimput(int clientSocket){

    while(true){

    string input;
    cin >> input;
    if(input == "\x03"){
        break;
    }
    const char* message = input.c_str();
    

    if (send(clientSocket,
             message,
             strlen(message),
             0) == -1)
    {
        perror("send");
        close(clientSocket);
        break;       
    }

    cout << "Message sent!" << endl;



    }






}


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

    time_t agora = time(nullptr);
    tm* tempo_local = localtime(&agora);

    cout <<put_time(tempo_local,"%H:%M   ") << "Connected to server!" << endl;
    
    thread t1(readimput, clientSocket);
    t1.join();

    close(clientSocket);

    return 0;
}