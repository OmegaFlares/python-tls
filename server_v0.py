from socket import socket, AF_INET, SOCK_STREAM
from ssl import SSLContext, SSLSocket, PROTOCOL_TLS_SERVER


ip = '127.0.0.1'
port = 8443
context = SSLContext(PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert.pem', 'key.pem')

with socket(AF_INET, SOCK_STREAM) as server:
    server.bind((ip, port))
    server.listen(1)
    with context.wrap_socket(server, server_side=True) as tls:
        connection, address = tls.accept()
        print(f'Connected by {address}\n')

        print(f"Available cipher methods: {SSLSocket.shared_ciphers()} \n")
        print(f"Cipher in use: {SSLSocket.cipher()} \n")

        data = connection.recv(1024)
        print(f'Client Says: {data}')

        connection.sendall(b"You're welcome")
