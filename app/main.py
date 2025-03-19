import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    clientSocket, clientAddress = server_socket.accept()  # wait for client
    # Send a simple HTTP response
    request = clientSocket.recv(1024)  # receive the client request
    request = request.decode("utf-8")
    print(f"Received request: {request}")
    requestLine, headers, body = request.split("\r\n", maxsplit=2)
    if requestLine.split()[1] == "/":
        clientSocket.sendall(b"HTTP/1.1 200 OK\r\n\r\nHello, World!")
    else:
        clientSocket.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")


if __name__ == "__main__":
    main()
