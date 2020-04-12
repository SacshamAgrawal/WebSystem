import socket

host = socket.gethostname()
port = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((host,port))
    print(f"Connected to ({host}:{port})")
    while True:
        msg = input(' -> ')
        sock.sendall(msg.encode())
        data = sock.recv(1024).decode()
        if not data:
            print("Server Disconnected...")
            break
        print(f"from server",data)
        