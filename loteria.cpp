#include <algorithm>
#include <random>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

struct ResultadoAposta {
  vector<int> aposta;
  vector<int> acertos;
};

struct ResultadoSorteio {
  vector<int> numerosSorteados;
  vector<ResultadoAposta> resultados;
};

class Loteria {
private:
  int inicio;
  int fim;
  int qtd;
  vector<vector<int>> apostas;
  mt19937 rng;

  void validarConfiguracao(int novoInicio, int novoFim, int novaQtd) const {
    if (novoInicio > novoFim) {
      throw invalid_argument("inicio nao pode ser maior que fim");
    }

    int totalNumeros = novoFim - novoInicio + 1;
    if (novaQtd <= 0) {
      throw invalid_argument("qtd deve ser maior que zero");
    }

    if (novaQtd > totalNumeros) {
      throw invalid_argument("qtd nao pode ser maior que o intervalo");
    }
  }

  void validarNumeroNoIntervalo(int numero) const {
    if (numero < inicio || numero > fim) {
      throw invalid_argument("aposta contem numero fora do intervalo");
    }
  }

public:
  Loteria()
      : inicio(0), fim(100), qtd(5), rng(random_device{}()) {}

  int getInicio() const { return inicio; }

  int getFim() const { return fim; }

  int getQtd() const { return qtd; }

  vector<vector<int>> getApostas() const { return apostas; }

  void configurarInicio(int novoInicio) {
    validarConfiguracao(novoInicio, fim, qtd);
    inicio = novoInicio;
  }

  void configurarFim(int novoFim) {
    validarConfiguracao(inicio, novoFim, qtd);
    fim = novoFim;
  }

  void configurarQtd(int novaQtd) {
    validarConfiguracao(inicio, fim, novaQtd);
    qtd = novaQtd;
  }

  void configurar(int novoInicio, int novoFim, int novaQtd) {
    validarConfiguracao(novoInicio, novoFim, novaQtd);
    inicio = novoInicio;
    fim = novoFim;
    qtd = novaQtd;
  }

  void registrarAposta(const vector<int> &numeros) {
    if (numeros.empty()) {
      throw invalid_argument("aposta nao pode ser vazia");
    }

    set<int> apostaUnica;
    for (int numero : numeros) {
      validarNumeroNoIntervalo(numero);
      apostaUnica.insert(numero);
    }

    apostas.emplace_back(apostaUnica.begin(), apostaUnica.end());
  }

  vector<int> sortearNumeros() {
    vector<int> universo;
    universo.reserve(fim - inicio + 1);

    for (int numero = inicio; numero <= fim; ++numero) {
      universo.push_back(numero);
    }

    shuffle(universo.begin(), universo.end(), rng);

    vector<int> sorteados(universo.begin(), universo.begin() + qtd);
    sort(sorteados.begin(), sorteados.end());

    return sorteados;
  }

  vector<ResultadoAposta> conferirApostas(const vector<int> &sorteados) const {
    vector<ResultadoAposta> resultados;
    set<int> sorteadosSet(sorteados.begin(), sorteados.end());

    for (const vector<int> &aposta : apostas) {
      ResultadoAposta resultado;
      resultado.aposta = aposta;

      for (int numero : aposta) {
        if (sorteadosSet.count(numero) > 0) {
          resultado.acertos.push_back(numero);
        }
      }

      resultados.push_back(resultado);
    }

    return resultados;
  }

  ResultadoSorteio realizarSorteio() {
    ResultadoSorteio resultado;
    resultado.numerosSorteados = sortearNumeros();
    resultado.resultados = conferirApostas(resultado.numerosSorteados);
    limparApostas();
    return resultado;
  }

  void limparApostas() { apostas.clear(); }

  bool temApostas() const { return !apostas.empty(); }
};

vector<int> extrairNumerosDaLinha(const string &linha) {
  stringstream stream(linha);
  vector<int> numeros;
  int numero;

  while (stream >> numero) {
    numeros.push_back(numero);
  }

  if (!stream.eof()) {
    throw invalid_argument("linha possui valor que nao e numero");
  }

  return numeros;
}
