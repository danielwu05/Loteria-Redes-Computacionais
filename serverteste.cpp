#include <arpa/inet.h>
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <netinet/in.h>
#include <sstream>
#include <string>
#include <sys/socket.h>
#include <sys/types.h>
#include <thread>
#include <unistd.h>
#include <vector>

#include "loteria.cpp"

using namespace std;

Loteria loteria;
mutex loteriaMutex;
mutex envioMutex;
mutex cicloMutex;
condition_variable cicloCv;
atomic<bool> servidorAtivo(true);

string horarioAtual() {
  time_t now = time(nullptr);
  tm *timeNow = localtime(&now);

  stringstream stream;
  stream << put_time(timeNow, "%H:%M");
  return stream.str();
}

string numerosParaTexto(const vector<int> &numeros) {
  stringstream stream;

  for (size_t i = 0; i < numeros.size(); ++i) {
    if (i > 0) {
      stream << " ";
    }
    stream << numeros[i];
  }

  return stream.str();
}

bool enviarLinha(int clientSocket, const string &linha) {
  lock_guard<mutex> lock(envioMutex);
  string mensagem = linha + "\n";
  return send(clientSocket, mensagem.c_str(), mensagem.size(), 0) != -1;
}

void processarLinha(int clientSocket, const string &linha) {
  if (linha.empty()) {
    return;
  }

  try {
    if (linha[0] == ':') {
      string comando;
      int valor;
      stringstream stream(linha);
      stream >> comando >> valor;

      if (!stream || (comando != ":inicio" && comando != ":fim" &&
                      comando != ":qtd")) {
        enviarLinha(clientSocket, "Comando invalido. Use :inicio N, :fim N ou :qtd N.");
        return;
      }

      {
        lock_guard<mutex> lock(loteriaMutex);

        if (comando == ":inicio") {
          loteria.configurarInicio(valor);
        } else if (comando == ":fim") {
          loteria.configurarFim(valor);
        } else {
          loteria.configurarQtd(valor);
        }
      }

      enviarLinha(clientSocket, "Configuracao atualizada: " + comando + " " +
                                    to_string(valor));
      return;
    }

    vector<int> numeros = extrairNumerosDaLinha(linha);

    {
      lock_guard<mutex> lock(loteriaMutex);
      loteria.registrarAposta(numeros);
    }

    enviarLinha(clientSocket, "Aposta registrada: " + numerosParaTexto(numeros));
  } catch (const exception &error) {
    enviarLinha(clientSocket, string("Erro: ") + error.what());
  }
}

void receberCliente(int clientSocket) {
  string pendente;
  char buffer[1024];

  while (servidorAtivo) {
    ssize_t bytesReceived = recv(clientSocket, buffer, sizeof(buffer) - 1, 0);

    if (bytesReceived == -1) {
      perror("recv");
      servidorAtivo = false;
      break;
    }

    if (bytesReceived == 0) {
      cout << "Cliente desconectou do servidor" << endl;
      servidorAtivo = false;
      cicloCv.notify_one();
      break;
    }

    buffer[bytesReceived] = '\0';
    pendente += buffer;

    size_t posicaoQuebra;
    while ((posicaoQuebra = pendente.find('\n')) != string::npos) {
      string linha = pendente.substr(0, posicaoQuebra);
      pendente.erase(0, posicaoQuebra + 1);

      if (!linha.empty() && linha.back() == '\r') {
        linha.pop_back();
      }

      cout << "Cliente enviou: " << linha << endl;
      processarLinha(clientSocket, linha);
    }
  }
}

void sortearPeriodicamente(int clientSocket) {
  while (servidorAtivo) {
    unique_lock<mutex> lock(cicloMutex);
    cicloCv.wait_for(lock, chrono::minutes(1),
                     [] { return !servidorAtivo.load(); });
    lock.unlock();

    if (!servidorAtivo) {
      break;
    }

    ResultadoSorteio resultado;
    bool tinhaApostas;

    {
      lock_guard<mutex> lock(loteriaMutex);
      tinhaApostas = loteria.temApostas();
      resultado = loteria.realizarSorteio();
    }

    stringstream mensagem;
    mensagem << "Sorteio: " << numerosParaTexto(resultado.numerosSorteados);

    if (!tinhaApostas) {
      mensagem << "\nNenhuma aposta registrada neste ciclo.";
    } else {
      for (size_t i = 0; i < resultado.resultados.size(); ++i) {
        const ResultadoAposta &aposta = resultado.resultados[i];
        mensagem << "\nAposta " << (i + 1) << " ["
                 << numerosParaTexto(aposta.aposta) << "] acertou "
                 << aposta.acertos.size() << " numero(s)";

        if (!aposta.acertos.empty()) {
          mensagem << ": " << numerosParaTexto(aposta.acertos);
        }
      }
    }

    if (!enviarLinha(clientSocket, mensagem.str())) {
      servidorAtivo = false;
      break;
    }
  }
}

int main() {
  int serverSocket = socket(AF_INET, SOCK_STREAM, 0);

  if (serverSocket == -1) {
    perror("socket");
    return 1;
  }

  int reuse = 1;
  setsockopt(serverSocket, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

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

  cout << "Servidor aguardando na porta 9090..." << endl;

  int clientSocket = accept(serverSocket, nullptr, nullptr);

  if (clientSocket == -1) {
    perror("accept");
    close(serverSocket);
    return 1;
  }

  cout << horarioAtual() << " - Cliente conectado!" << endl;
  enviarLinha(clientSocket, horarioAtual() + ": CONECTADO!!");

  thread t1(receberCliente, clientSocket);
  thread t2(sortearPeriodicamente, clientSocket);

  t1.join();
  servidorAtivo = false;
  cicloCv.notify_one();

  shutdown(clientSocket, SHUT_RDWR);
  close(clientSocket);
  close(serverSocket);

  if (t2.joinable()) {
    t2.join();
  }

  return 0;
}
