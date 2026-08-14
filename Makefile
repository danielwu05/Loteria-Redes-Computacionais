all: client server

client: clienteteste.cpp
	mkdir -p build
	g++ -std=c++20 -Wall -Wextra -pedantic clienteteste.cpp -pthread -o build/cliente

server: serverteste.cpp loteria.cpp
	mkdir -p build
	g++ -std=c++20 -Wall -Wextra -pedantic serverteste.cpp -pthread -o build/server
