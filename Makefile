all: client server

client: clienteteste.cpp
	g++ clienteteste.cpp -o build/client

server: serverteste.cpp
	g++ serverteste.cpp -o build/server

