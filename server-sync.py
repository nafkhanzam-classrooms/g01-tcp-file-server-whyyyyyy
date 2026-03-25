import socket
import os

clients = []
FILES_DIR = "server_files"

if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

class Server:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 50000
        self.size = 1024

    def broadcast(self, current_client, message):
        for c in clients:
            if c != current_client:
                try:
                    c.send(b"MSG:" + message)
                except:
                    pass

    def handle_client(self, client_sock, client_addr):
        print(f"[CONNECTED] {client_addr}")
        clients.append(client_sock)

        try:
            while True:
                data = client_sock.recv(self.size)
                if not data:
                    break

                message = data.decode(errors="ignore").strip()

                if message.startswith("/list"):
                    files = os.listdir(FILES_DIR)
                    response = "Files on Server:\n" + ("\n".join(files) if files else "(No files)")
                    client_sock.send(response.encode())

                elif message.startswith("/upload"):
                    parts = message.split(" ", 1)
                    if len(parts) < 2:
                        client_sock.send(b"Upload Failed : Invalid command")
                        continue

                    filename = os.path.basename(parts[1])
                    filepath = os.path.join(FILES_DIR, filename)

                    if os.path.exists(filepath):
                        client_sock.send(b"Upload Failed : File already exists")
                        continue

                    client_sock.send(b"READY")
                    
                    try:
                        filesize_data = client_sock.recv(8)
                        filesize = int.from_bytes(filesize_data, byteorder='big')
                        
                        received_bytes = 0
                        with open(filepath, "wb") as f:
                            while received_bytes < filesize:
                                to_read = min(self.size, filesize - received_bytes)
                                chunk = client_sock.recv(to_read)
                                if not chunk:
                                    break
                                f.write(chunk)
                                received_bytes += len(chunk)

                        client_sock.send(b"Upload Completed : File uploaded successfully")
                    except Exception as e:
                        print("[UPLOAD ERROR]", e)
                        if os.path.exists(filepath):
                            os.remove(filepath)

                elif message.startswith("/download"):
                    parts = message.split(" ", 1)
                    if len(parts) < 2:
                        client_sock.send(b"Download Failed : Invalid command")
                        continue

                    filename = os.path.basename(parts[1])
                    filepath = os.path.join(FILES_DIR, filename)

                    if not os.path.exists(filepath):
                        client_sock.send(b"Download Failed : File not found")
                        continue

                    client_sock.send(b"READY")
                    response = client_sock.recv(self.size)
                    filesize = os.path.getsize(filepath)
                    client_sock.send(filesize.to_bytes(8, byteorder='big'))

                    with open(filepath, "rb") as f:
                        while chunk := f.read(self.size):
                            client_sock.send(chunk)

                else:
                    print(f"[MSG] {client_addr}: {message}")
                    self.broadcast(client_sock, message.encode())

        finally:
            print(f"[DISCONNECTED] {client_addr}")
            if client_sock in clients:
                clients.remove(client_sock)
            client_sock.close()

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)

        print(f"[LISTENING] {self.host}:{self.port}")

        try:
            while True:
                client_sock, client_addr = server.accept()
                self.handle_client(client_sock, client_addr)
        except KeyboardInterrupt:
            print("\n[SHUTDOWN]")
        finally:
            server.close()

if __name__ == "__main__":
    Server().run()