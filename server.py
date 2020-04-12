import socket

host = socket.gethostname()
port = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind((host,port))
    sock.listen(1)
    while True:
        conn, addr = sock.accept()
        print(f"Connected to {addr}")
        while True:
            data = conn.recv(1024).decode()
            if not data:
                print("Client Disconnected")
                break;
            print(f"from {addr}:",data)
            data = input(' -> ').encode()
            conn.sendall(data)

        