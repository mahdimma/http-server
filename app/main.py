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
    requestLine, remain = request.split("\r\n", maxsplit=1)
    headers, body = remain.split("\r\n\r\n", maxsplit=1)
    originFormAddress = requestLine.split()[1]
    if originFormAddress == "/":
        clientSocket.sendall(
            b"HTTP/1.1 200 OK\r\nhost: localhost:4221\r\n\r\nHello, World!"
        )
    elif originFormAddress.startswith("/echo"):
        clientSocket.sendall(
            f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(originFormAddress) - 6}\r\n\r\n{originFormAddress[6:]}".encode()
        )
    elif originFormAddress.startswith("/user-agent"):
        userAgentText = headers.split("\r\n")[1].split(": ")[1]
        clientSocket.sendall(
            f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(userAgentText)}\r\n\r\n{userAgentText}".encode()
        )
    else:
        clientSocket.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")


if __name__ == "__main__":
    main()
