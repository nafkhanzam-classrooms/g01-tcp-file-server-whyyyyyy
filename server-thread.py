import socket
import threading
import os

clients = []
clients_lock = threading.Lock()
FILES_DIR = "server_files"

if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)


class ClientThread(threading.Thread):
    def __init__(self, client, address):
        super().__init__()
        self.client = client
        self.address = address
        self.size = 1024

    def broadcast(self, message):
        with clients_lock:
            for c in clients:
                if c != self.client:
                    try:
                        c.send(b"MSG:" + message)
                    except:
                        pass

    def run(self):
        print(f"[CONNECTED] {self.address}")

        with clients_lock:
            clients.append(self.client)

        try:
            while True:
                data = self.client.recv(self.size)
                if not data:
                    break

                message = data.decode(errors="ignore").strip()

                # LIST
                if message.startswith("/list"):
                    files = os.listdir(FILES_DIR)
                    if files:
                        response = "Files on Server:\n" + "\n".join(files)
                    else:
                        response = "Files on Server:\n(No files)"
                    self.client.send(response.encode())

                # UPLOAD
                elif message.startswith("/upload"):
                    parts = message.split(" ", 1)
                    if len(parts) < 2:
                        self.client.send(b"Upload Failed : Invalid command")
                        continue

                    filename = os.path.basename(parts[1])
                    filepath = os.path.join(FILES_DIR, filename)

                    if os.path.exists(filepath):
                        self.client.send(b"Upload Failed : File already exists")
                        continue

                    self.client.send(b"READY")
                    
                    try:
                        filesize_data = self.client.recv(8)
                        filesize = int.from_bytes(filesize_data, byteorder='big')
                        
                        received_bytes = 0
                        with open(filepath, "wb") as f:
                            while received_bytes < filesize:
                                to_read = min(self.size, filesize - received_bytes)
                                chunk = self.client.recv(to_read)
                                if not chunk:
                                    break
                                f.write(chunk)
                                received_bytes += len(chunk)

                        self.client.send(b"Upload Completed : File uploaded successfully")
                    except Exception as e:
                        print("[UPLOAD ERROR]", e)
                        if os.path.exists(filepath):
                            os.remove(filepath)

                # DOWNLOAD
                elif message.startswith("/download"):
                    parts = message.split(" ", 1)
                    if len(parts) < 2:
                        self.client.send(b"Download Failed : Invalid command")
                        continue

                    filename = os.path.basename(parts[1])
                    filepath = os.path.join(FILES_DIR, filename)

                    if not os.path.exists(filepath):
                        self.client.send(b"Download Failed : File not found")
                        continue

                    self.client.send(b"READY")
                    response = self.client.recv(self.size)
                    
                    filesize = os.path.getsize(filepath)
                    self.client.send(filesize.to_bytes(8, byteorder='big'))

                    with open(filepath, "rb") as f:
                        while chunk := f.read(self.size):
                            self.client.send(chunk)

                # CHAT
                else:
                    print(f"[MSG] {self.address}: {message}")
                    self.broadcast(message.encode())

        finally:
            print(f"[DISCONNECTED] {self.address}")
            with clients_lock:
                if self.client in clients:
                    clients.remove(self.client)
            self.client.close()


class Server:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 50000

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)

        print(f"[LISTENING] {self.host}:{self.port}")

        try:
            while True:
                client_sock, client_addr = server.accept()
                thread = ClientThread(client_sock, client_addr)
                thread.start()

        except KeyboardInterrupt:
            print("\n[SHUTDOWN]")
        finally:
            server.close()


if __name__ == "__main__":
    Server().run()