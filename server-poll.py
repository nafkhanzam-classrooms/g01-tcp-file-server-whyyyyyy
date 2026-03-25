import socket
import select
import os

FILES_DIR = "server_files"
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

class Server:
    def __init__(self, host='127.0.0.1', port=50000):
        self.host = host
        self.port = port
        self.clients = {}  # fd -> socket object
        self.addresses = {} # fd -> address
        self.size = 1024

    def broadcast(self, message, sender_fd):
        for fd, sock in self.clients.items():
            if fd != sender_fd:
                try:
                    sock.send(b"MSG:" + message)
                except:
                    pass

    def handle_request(self, client_sock, fd):
        try:
            data = client_sock.recv(self.size)
            if not data:
                return False

            message = data.decode(errors="ignore").strip()
            addr = self.addresses[fd]

            if message.startswith("/list"):
                files = os.listdir(FILES_DIR)
                response = "Files on Server:\n" + ("\n".join(files) if files else "(No files)")
                client_sock.send(response.encode())

            elif message.startswith("/upload"):
                parts = message.split(" ", 1)
                if len(parts) < 2:
                    client_sock.send(b"Upload Failed : Invalid command")
                else:
                    filename = os.path.basename(parts[1])
                    filepath = os.path.join(FILES_DIR, filename)
                    if os.path.exists(filepath):
                        client_sock.send(b"Upload Failed : File already exists")
                    else:
                        client_sock.send(b"READY")
                        client_sock.setblocking(True)
                        filesize_data = client_sock.recv(8)
                        filesize = int.from_bytes(filesize_data, byteorder='big')
                        received_bytes = 0
                        with open(filepath, "wb") as f:
                            while received_bytes < filesize:
                                to_read = min(self.size, filesize - received_bytes)
                                chunk = client_sock.recv(to_read)
                                if not chunk: break
                                f.write(chunk)
                                received_bytes += len(chunk)
                        client_sock.send(b"Upload Completed : File uploaded successfully")
                        client_sock.setblocking(False)

            elif message.startswith("/download"):
                parts = message.split(" ", 1)
                if len(parts) < 2:
                    client_sock.send(b"Download Failed : Invalid command")
                else:
                    filename = os.path.basename(parts[1])
                    filepath = os.path.join(FILES_DIR, filename)
                    if not os.path.exists(filepath):
                        client_sock.send(b"Download Failed : File not found")
                    else:
                        client_sock.send(b"READY")
                        client_sock.setblocking(True)
                        client_sock.recv(self.size) # Wait for client ack
                        filesize = os.path.getsize(filepath)
                        client_sock.send(filesize.to_bytes(8, byteorder='big'))
                        with open(filepath, "rb") as f:
                            while chunk := f.read(self.size):
                                client_sock.send(chunk)
                        client_sock.setblocking(False)

            else:
                print(f"[MSG] {addr}: {message}")
                self.broadcast(message.encode(), fd)
            
            return True
        except Exception as e:
            print(f"[ERROR] {e}")
            return False

    def run(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen(5)
        server_sock.setblocking(False)

        poller = select.poll()
        poller.register(server_sock, select.POLLIN)

        print(f"[LISTENING] {self.host}:{self.port}")

        try:
            while True:
                events = poller.poll()
                for fd, event in events:
                    if fd == server_sock.fileno():
                        client_sock, addr = server_sock.accept()
                        print(f"[CONNECTED] {addr}")
                        client_sock.setblocking(False)
                        self.clients[client_sock.fileno()] = client_sock
                        self.addresses[client_sock.fileno()] = addr
                        poller.register(client_sock, select.POLLIN)
                    
                    elif event & select.POLLIN:
                        client_sock = self.clients[fd]
                        if not self.handle_request(client_sock, fd):
                            print(f"[DISCONNECTED] {self.addresses[fd]}")
                            poller.unregister(fd)
                            client_sock.close()
                            del self.clients[fd]
                            del self.addresses[fd]
                            
                    elif event & (select.POLLHUP | select.POLLERR):
                        poller.unregister(fd)
                        self.clients[fd].close()
                        del self.clients[fd]
                        del self.addresses[fd]

        except KeyboardInterrupt:
            print("\n[SHUTDOWN]")
        finally:
            server_sock.close()

if __name__ == "__main__":
    Server().run()