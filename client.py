import socket
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
            print("\n Server has closed the connection. Press 'Enter' key to disconnect.")
            return
        elif buf == "::quit_confirm":
            print("\n Connection to server closed.")
            return
        else:
            print(f" >>> Server sent: {buf} ") 
            buf = b'' 
    return 


def send_com():
    global flag_quit
    while flag_quit:
        msg = input()
        if not msg: 
            pass
        elif msg == "::quit":
            conn.send(bytes("::quit", "utf-8")) 
            flag_quit = False
            return
        else:
            conn.send(bytes(msg, "utf-8")) 
            print(f" >>> Client sent: {msg} ") 
            msg = ""   
    return



##########################


host_addr = '127.0.0.1'
host_port = 8082
server_sni_hostname = 'BOB'
server_cert = 'EC.crt'
client_cert = 'ALICE.crt'
client_key = 'ALICE.key'


context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.minimum_version = ssl.TLSVersion.TLSv1_3
context.maximum_version = ssl.TLSVersion.TLSv1_3

print(" The following ciphers are available:")
for cs in context.get_ciphers(): print(f"  - {cs['name']}")
print("\n")

context.load_verify_locations(server_cert)
# context.load_cert_chain(certfile=client_cert, keyfile=client_key)
context.load_cert_chain(certfile=client_cert, keyfile=client_key, password=b'1234')


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(s, server_side=False, server_hostname=server_sni_hostname)
conn.connect((host_addr, host_port)) 
print(f"\n Connected to server '{server_sni_hostname}'.\n")
print(f" Cipher details: '{conn.cipher()[0]}', '{conn.cipher()[1]}'")
print(" SSL established. Peer certificate:")
peer_cert = conn.getpeercert()
pprint.pprint(peer_cert)
peer_CN = [i[0][1] for i in peer_cert["subject"] if i[0][0]=="commonName"]
print("\n", "-"*115)
print(f"\n You are now chatting with '{peer_CN[0]}'. Type '::quit' to disconnect and terminate program.\n")

try:
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
    conn.close()