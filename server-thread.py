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
                        with open(filepath, "wb") as f:
                            while True:
                                chunk = self.client.recv(self.size)
                                if b"__EOF__" in chunk:
                                    chunk = chunk.replace(b"__EOF__", b"")
                                    f.write(chunk)
                                    break
                                f.write(chunk)

                        self.client.send(b"Upload Completed")

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

                    with open(filepath, "rb") as f:
                        while True:
                            chunk = f.read(self.size)
                            if not chunk:
                                break
                            self.client.send(chunk)

                    self.client.send(b"__EOF__")

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