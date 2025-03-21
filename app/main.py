import socket  # noqa: F401
import threading
import sys
import gzip


SUPPORTED_COMPRESION = ["gzip"]


def compress(data: str, compression) -> bytes:
    return gzip.compress(data.encode("utf-8"))


def header_parser(headers: str):
    headers = headers.split("\r\n")
    headers_dict = {}
    for header in headers:
        key, value = header.split(": ")
        headers_dict[key] = value
    return headers_dict


def handle_request(clientSocket: socket.socket, path: str) -> None:
    try:
        request = clientSocket.recv(1024)  # receive the client request
        request = request.decode("utf-8")
        print(f"Received request: {request}")
        requestLine, remain = request.split("\r\n", maxsplit=1)
        headers, body = remain.split("\r\n\r\n", maxsplit=1)
        httpMethod = requestLine.split()[0]
        originFormAddress = requestLine.split()[1]
        match httpMethod:
            case "POST":
                if originFormAddress.startswith("/files"):
                    if not path:
                        clientSocket.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
                        return
                    with open(path + originFormAddress[7:], "w") as file:
                        file.write(body)
                    clientSocket.sendall(b"HTTP/1.1 201 Created\r\n\r\n")
            case "GET":
                if originFormAddress == "/":
                    clientSocket.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
                elif originFormAddress.startswith("/echo"):
                    global SUPPORTED_COMPRESION
                    headers = header_parser(headers)
                    try:
                        compressed = False
                        for compression in headers["Accept-Encoding"].split(", "):
                            if compression in SUPPORTED_COMPRESION:
                                strFromAddress = compress(
                                    originFormAddress[6:], compression
                                )
                                clientSocket.send(
                                    f"HTTP/1.1 200 OK\r\nContent-Encoding: {compression}\r\nContent-Type: text/plain\r\nContent-Length: {len(strFromAddress)}\r\n\r\n".encode()
                                    + strFromAddress
                                )
                                compressed = True
                                break
                        if not compressed:
                            clientSocket.sendall(
                                f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(originFormAddress) - 6}\r\n\r\n{originFormAddress[6:]}".encode()
                            )
                    except KeyError as e:
                        # If the client does not support compression (basic task)
                        clientSocket.sendall(
                            f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(originFormAddress) - 6}\r\n\r\n{originFormAddress[6:]}".encode()
                        )
                elif originFormAddress.startswith("/user-agent"):
                    userAgentText = headers.split("\r\n")[1].split(": ")[1]
                    clientSocket.sendall(
                        f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(userAgentText)}\r\n\r\n{userAgentText}".encode()
                    )
                elif originFormAddress.startswith("/file"):
                    if not path:
                        clientSocket.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
                        return
                    try:
                        with open(path + originFormAddress[6:], "r") as file:
                            fileContent = file.read()
                            clientSocket.sendall(
                                f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(fileContent)}\r\n\r\n{fileContent}".encode()
                            )
                    except FileNotFoundError:
                        clientSocket.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
                else:
                    clientSocket.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

    finally:
        clientSocket.close()


def main(path: str = None):
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    # Send a simple HTTP response
    while True:
        clientSocket, clientAddress = server_socket.accept()  # wait for client
        threading.Thread(
            target=handle_request,
            args=(
                clientSocket,
                path,
            ),
        ).start()


if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[2])
    else:
        main()
