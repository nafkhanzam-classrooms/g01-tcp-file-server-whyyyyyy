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
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.setblocking(False)
        self.inputs = [self.server_sock]
        self.clients = []
        self.size = 1024

    def broadcast(self, message, sender_sock):
        for c in self.clients:
            if c != sender_sock:
                try:
                    c.send(b"MSG:" + message)
                except:
                    self.disconnect_client(c)

    def disconnect_client(self, sock):
        print(f"[DISCONNECTED] Client")
        if sock in self.inputs:
            self.inputs.remove(sock)
        if sock in self.clients:
            self.clients.remove(sock)
        sock.close()

    def handle_request(self, sock):
        try:
            sock.setblocking(True)
            data = sock.recv(self.size)
            if not data:
                self.disconnect_client(sock)
                return

            message = data.decode(errors="ignore").strip()

            if message.startswith("/list"):
                files = os.listdir(FILES_DIR)
                response = "Files on Server:\n" + ("\n".join(files) if files else "(No files)")
                sock.send(response.encode())

            elif message.startswith("/upload"):
                parts = message.split(" ", 1)
                if len(parts) < 2:
                    sock.send(b"Upload Failed : Invalid command")
                    return

                filename = os.path.basename(parts[1])
                filepath = os.path.join(FILES_DIR, filename)

                if os.path.exists(filepath):
                    sock.send(b"Upload Failed : File already exists")
                    return

                sock.send(b"READY")
                
                filesize_data = sock.recv(8)
                if not filesize_data: return
                filesize = int.from_bytes(filesize_data, byteorder='big')

                received_bytes = 0
                with open(filepath, "wb") as f:
                    while received_bytes < filesize:
                        to_read = min(self.size, filesize - received_bytes)
                        chunk = sock.recv(to_read)
                        if not chunk: break
                        f.write(chunk)
                        received_bytes += len(chunk)
                
                sock.send(b"Upload Completed : File uploaded successfully")

            elif message.startswith("/download"):
                parts = message.split(" ", 1)
                if len(parts) < 2:
                    sock.send(b"Download Failed : Invalid command")
                    return

                filename = os.path.basename(parts[1])
                filepath = os.path.join(FILES_DIR, filename)

                if not os.path.exists(filepath):
                    sock.send(b"Download Failed : File not found")
                    return

                sock.send(b"READY")
                ack = sock.recv(self.size) # Wait for client ready
                
                filesize = os.path.getsize(filepath)
                sock.send(filesize.to_bytes(8, byteorder='big'))

                with open(filepath, "rb") as f:
                    while chunk := f.read(self.size):
                        sock.send(chunk)

            else:
                print(f"[MSG] {sock.getpeername()}: {message}")
                self.broadcast(message.encode(), sock)

            sock.setblocking(False)

        except Exception as e:
            print(f"[ERROR] {e}")
            self.disconnect_client(sock)

    def run(self):
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(5)
        print(f"[LISTENING] {self.host}:{self.port}")

        try:
            while True:
                readable, _, exceptional = select.select(self.inputs, [], self.inputs)

                for s in readable:
                    if s is self.server_sock:
                        conn, addr = s.accept()
                        print(f"[CONNECTED] {addr}")
                        conn.setblocking(False)
                        self.inputs.append(conn)
                        self.clients.append(conn)
                    else:
                        self.handle_request(s)

                for s in exceptional:
                    self.disconnect_client(s)

        except KeyboardInterrupt:
            print("\n[SHUTDOWN]")
        finally:
            for s in self.inputs:
                s.close()

if __name__ == "__main__":
    Server().run()