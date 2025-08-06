import socket
HOST=''
PORT=10001

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.connect((HOST,PORT))
    s.send("rx".encode('utf-8'))
    data=s.recv(1024).decode('utf-8')
    print(data)
