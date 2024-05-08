import socket
from socket import AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET, SHUT_RDWR
import ssl
import threading
import pprint


##########################

def receive_com():
    global flag_quit
    buf = b''
    while flag_quit:
        data = conn.recv(4096)
        buf = str(data, "utf-8")
        if not buf:
            pass
        elif buf == "::quit":
            conn.send(bytes("::quit_confirm", "utf-8")) 
            flag_quit = False
            print("\n Client has closed the connection. Press 'Enter' key to disconnect.")
            return
        elif buf == "::quit_confirm":
            print("\n Connection to server closed.")
            return
        else:
            print(f" >>> Client sent: {buf} ") 
            buf = b'' 
    return 


def send_com():
    global flag_exit
    global flag_quit
    while flag_quit:
        msg = input()
        if not msg: 
            pass
        elif msg == "::exit":
            conn.send(bytes("::quit", "utf-8")) 
            flag_quit = False
            flag_exit = False
        elif msg == "::quit":
            conn.send(bytes("::quit", "utf-8")) 
            flag_quit = False
            return
        else:
            conn.send(bytes(msg, "utf-8")) 
            print(f" >>> Server sent: {msg} ")
            msg = ""   
    return



##########################


listen_addr = '127.0.0.1'
listen_port = 8082
server_cert = 'BOB.crt'
server_key = 'BOB.key'
client_certs = 'EC.crt'


context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.minimum_version = ssl.TLSVersion.TLSv1_3
context.maximum_version = ssl.TLSVersion.TLSv1_3
# for cs in context.get_ciphers(): print(f"  - {cs['name']}")

# context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
# context.load_cert_chain(certfile=server_cert, keyfile=server_key)
context.load_cert_chain(certfile=server_cert, keyfile=server_key, password=b'1234')
context.load_verify_locations(cafile=client_certs)

print(" The following ciphers are available:")
for cs in context.get_ciphers(): print(f"  - {cs['name']}")




bindsocket = socket.socket()
bindsocket.bind((listen_addr, listen_port))
bindsocket.listen(5)

flag_exit = True
while flag_exit:
    print("\n Waiting for client...\n")
    newsocket, fromaddr = bindsocket.accept()
    print(" Client connected: {}:{}".format(fromaddr[0], fromaddr[1]))
    conn = context.wrap_socket(newsocket, server_side=True)
    # print("cipher -> ", conn.cipher())
    print(f" Cipher details: '{conn.cipher()[0]}', '{conn.cipher()[1]}'")
    # print("SSL established. Peer: {}\n".format(conn.getpeercert()))
    print(" SSL established. Peer certificate:")
    peer_cert = conn.getpeercert()
    pprint.pprint(peer_cert)
    peer_CN = [i[0][1] for i in peer_cert["subject"] if i[0][0]=="commonName"]
    print("\n", "-"*115)
    print(f"\n You are now chatting with '{peer_CN[0]}'. Type '::quit' to disconnect client or '::exit' to terminate program.\n")

    try:
        # while True:
            # data = conn.recv(4096)
            # if data:
            #     # Client sent us data. Append to buffer
            #     buf += data
            # else:
            #     # No more data from client. Show buffer and close connection.
            #     print("Received:", buf)
            #     break
        flag_quit = True
        recv = threading.Thread(target=receive_com)
        send = threading.Thread(target=send_com)
        recv.start()
        send.start()
        recv.join()
        send.join()

    finally:
        print("\n", "-"*115)
        print("\n Disconnected.\n")
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()