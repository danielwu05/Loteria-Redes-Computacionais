# 🎰 Loteria - Redes de Computadores

Sistema de loteria desenvolvido como **Projeto Prático 1** da disciplina de **Redes de Computadores**, do curso de **Engenharia de Computação**.

O projeto implementa uma aplicação **cliente/servidor utilizando sockets TCP**, permitindo que um usuário configure uma loteria, envie apostas através do cliente e receba do servidor os números sorteados e os números acertados.

O sistema utiliza **multithreading** tanto no cliente quanto no servidor, permitindo que envio e recebimento de dados ocorram de maneira independente.

---

## 📌 Objetivo

O objetivo do projeto é aplicar conceitos de Redes de Computadores por meio da implementação de uma aplicação distribuída que utiliza:

* Comunicação cliente/servidor;
* Sockets TCP;
* Threads;
* Troca de mensagens pela rede;
* Processamento de comandos;
* Manipulação de apostas;
* Sorteio aleatório de números.

---

## ⚙️ Funcionamento

A aplicação é dividida em dois programas principais:

* **Cliente:** recebe comandos e apostas digitados pelo usuário e apresenta as respostas enviadas pelo servidor.
* **Servidor:** recebe e interpreta as mensagens do cliente, realiza os sorteios e envia os resultados.

Ao iniciar o cliente, uma conexão TCP é estabelecida com o servidor.

Após a conexão, o servidor envia uma mensagem de confirmação contendo o horário:

```text
HH:MM - CONECTADO!!
```

Depois disso, cliente e servidor passam a executar duas threads simultaneamente.

---

## 🧵 Threads

### Cliente

O cliente possui duas threads principais:

**Thread de entrada**

Responsável por:

1. Aguardar a entrada do usuário pelo teclado;
2. Receber comandos de configuração ou apostas;
3. Enviar a mensagem para o servidor pelo socket;
4. Voltar a aguardar novas entradas.

**Thread de recebimento**

Responsável por:

1. Permanecer aguardando mensagens enviadas pelo servidor;
2. Receber os dados através do socket;
3. Exibir o conteúdo recebido na tela;
4. Continuar aguardando novas mensagens.

Dessa forma, o cliente pode receber informações do servidor independentemente da entrada do usuário.

---

### Servidor

O servidor também possui duas threads principais.

**Thread de processamento**

Responsável por receber os dados enviados pelo cliente e identificar se a mensagem corresponde a:

* um comando de configuração;
* uma aposta;
* uma entrada inválida.

Os comandos alteram os parâmetros da loteria, enquanto as apostas são convertidas para números e armazenadas para posterior comparação com o resultado do sorteio.

**Thread de resultados**

Responsável por aguardar o intervalo definido para o sorteio e posteriormente enviar ao cliente:

* os números apostados;
* os números sorteados;
* os números acertados.

Após o envio do resultado, os dados referentes à rodada são apagados e o sistema pode iniciar um novo ciclo.

> Atualmente o intervalo utilizado no código é de **10 segundos**, facilitando os testes da aplicação. Na especificação original do projeto, o intervalo previsto para cada sorteio é de **1 minuto**.

---

## 🎲 Configuração da loteria

Caso nenhuma configuração seja realizada pelo usuário, a loteria utiliza os seguintes valores padrão:

```text
Início: 0
Fim:    100
Qtd:    5
```

Isso significa que serão sorteados **5 números diferentes entre 0 e 100**.

A configuração pode ser alterada através do cliente utilizando comandos iniciados por `:`.

### Alterar início do intervalo

```text
:inicio <numero>
```

Exemplo:

```text
:inicio 1
```

### Alterar final do intervalo

```text
:fim <numero>
```

Exemplo:

```text
:fim 60
```

### Alterar quantidade de números sorteados

```text
:qtd <numero>
```

Exemplo:

```text
:qtd 6
```

Com esses três comandos:

```text
:inicio 1
:fim 60
:qtd 6
```

a loteria passa a sortear **6 números entre 1 e 60**.

---

## 🎫 Realizando uma aposta

Para realizar uma aposta, basta digitar os números separados por espaços.

Exemplo:

```text
4 12 25 32 48
```

Entradas formadas apenas por números são interpretadas pelo servidor como apostas.

Comandos, por outro lado, começam com `:`.

---

## 🏆 Resultado

Quando ocorre o sorteio, o servidor compara os números apostados com os números sorteados.

O cliente recebe uma mensagem semelhante a:

```text
user guess: [4, 12, 25, 32, 48]

casino results: [4, 17, 25, 39, 56]

correct numbers: [4, 25]
```

Nesse exemplo, o usuário acertou os números:

```text
4 25
```

Após o resultado, os dados da rodada são limpos para permitir novas apostas.

---

## 🎯 Sorteio dos números

A lógica responsável pela loteria está implementada na classe `Lottery`.

Por padrão:

```python
initial = 0
final = 100
count = 5
```

O sorteio utiliza `random.sample()`, garantindo que um mesmo número não seja sorteado mais de uma vez dentro da mesma rodada.

A classe também é responsável por comparar os números apostados com os números sorteados e retornar somente os acertos.

---

## 📁 Estrutura do projeto

```text
Loteria-Redes-Computacionais/
│
├── client.py
├── clientObj.py
├── server.py
├── serverObj.py
├── lottery.py
├── .gitignore
└── README.md
```

### `client.py`

Ponto de entrada da aplicação cliente.

Define:

```text
Host: localhost
Porta: 8080
```

Cria uma instância de `Client` e inicia sua execução.

### `clientObj.py`

Contém a implementação do cliente.

É responsável por:

* criação do socket TCP;
* conexão ao servidor;
* thread de leitura do teclado;
* thread de recebimento de mensagens;
* envio de comandos e apostas;
* encerramento da conexão.

### `server.py`

Ponto de entrada do servidor.

Cria uma instância de `Server` e inicializa as duas threads responsáveis por:

```text
process_input
send_results
```

### `serverObj.py`

Contém a implementação principal do servidor.

É responsável por:

* criação do socket;
* `bind`;
* `listen`;
* `accept`;
* recebimento de mensagens;
* interpretação de comandos;
* armazenamento das apostas;
* realização dos sorteios;
* envio dos resultados.

### `lottery.py`

Contém a classe `Lottery`, responsável pela lógica da loteria.

Principais operações:

```text
setting_initial()
setting_final()
setting_count()
sorting_numbers()
checking_numbers()
```

---

## 🌐 Comunicação pela rede

O projeto utiliza sockets do tipo:

```python
socket.AF_INET
socket.SOCK_STREAM
```

Portanto, a comunicação é realizada utilizando:

```text
IPv4 + TCP
```

O servidor utiliza a porta:

```text
8080
```

e, atualmente, cliente e servidor estão configurados para execução na mesma máquina através de:

```text
localhost
```

Fluxo simplificado:

```text
CLIENTE                                  SERVIDOR

socket()                                 socket()
   │                                        │
   │                                     bind()
   │                                        │
   │                                    listen()
   │                                        │
connect() ─────────────────────────────> accept()
   │                                        │
   │ <──────── confirmação conexão ─────────│
   │                                        │
   ├── Thread 1 ───── comandos/apostas ────>│── Thread 1
   │                                        │
   │<──────────── resultados ───────────────│── Thread 2
   └── Thread 2                             │
```

---

## ▶️ Como executar

### Requisitos

É necessário possuir:

```text
Python 3
```

O projeto utiliza apenas bibliotecas presentes na biblioteca padrão do Python.

---

### 1. Clone o repositório

```bash
git clone https://github.com/danielwu05/Loteria-Redes-Computacionais.git
```

Entre na pasta:

```bash
cd Loteria-Redes-Computacionais
```

---

### 2. Inicie o servidor

Em um terminal:

```bash
python server.py
```

ou:

```bash
python3 server.py
```

O servidor ficará aguardando uma conexão na porta `8080`.

---

### 3. Inicie o cliente

Abra outro terminal e execute:

```bash
python client.py
```

ou:

```bash
python3 client.py
```

Após a conexão, será possível enviar comandos e apostas.

---

## 🧪 Exemplo de utilização

Cliente:

```text
10:35 - CONECTADO!!

> :inicio 1

> :fim 60

> :qtd 5

> 7 13 25 42 51
```

Após o sorteio, uma resposta semelhante será exibida:

```text
user guess: [7, 13, 25, 42, 51]
casino results: [7, 16, 25, 38, 54]
correct numbers: [7, 25]
```

Em seguida, uma nova rodada pode ser iniciada.

---

## 🔄 Fluxo geral da aplicação

```text
          CLIENTE
             │
             │ connect()
             ▼
          SERVIDOR
             │
             │ confirmação
             ▼
          CLIENTE
             │
      ┌──────┴──────┐
      │             │
   Thread 1      Thread 2
   teclado       receber
      │             ▲
      │             │
      ▼             │
          SERVIDOR
      ┌──────┴──────┐
      │             │
   Thread 1      Thread 2
   receber       sorteio
   apostas       resultado
      │             │
      └──────┬──────┘
             │
             ▼
         novo ciclo
```

---

## 🛠️ Tecnologias utilizadas

* Python
* Sockets TCP/IP
* IPv4
* Multithreading
* Biblioteca `socket`
* Biblioteca `threading`
* Biblioteca `random`
* Biblioteca `datetime`
* Biblioteca `time`

---

## 📚 Conceitos aplicados

Durante o desenvolvimento são aplicados conceitos estudados na disciplina de Redes de Computadores, principalmente:

* arquitetura cliente/servidor;
* comunicação TCP;
* criação e configuração de sockets;
* endereço IP e portas;
* transmissão de mensagens;
* concorrência através de threads;
* protocolo de aplicação;
* tratamento de entrada;
* sincronização entre comunicação e processamento.

---

## 📖 Disciplina

**Disciplina:** Redes de Computadores
**Curso:** Engenharia de Computação
**Atividade:** Projeto Prático 1
