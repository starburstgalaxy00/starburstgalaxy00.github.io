import socket
HOST=''
PORT=10001

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.connect((HOST,PORT))
    print("connection success")
    s.sendall(b'rx\r\n')
    data=s.recv(1024)
    print("received data:")
    print(data.decode(errors="ignore").strip())