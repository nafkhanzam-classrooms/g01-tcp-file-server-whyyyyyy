import socket
import threading
import os
import time

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 50000
SIZE = 1024
is_busy = False


def receive_messages(sock):
    global is_busy
    while True:
        try:
            if is_busy:
                time.sleep(0.5)
                continue

            data = sock.recv(SIZE)
            if not data:
                break

            if data.startswith(b"MSG:"):
                print("\n[CHAT]:", data[4:].decode())
            else:
                print("\n[SERVER]:", data.decode())

            print(">> ", end="", flush=True)

        except:
            break


def upload(sock, filepath):
    global is_busy

    if not os.path.exists(filepath):
        print("Upload Failed : File not found")
        return

    filename = os.path.basename(filepath)

    try:
        is_busy = True

        sock.send(f"/upload {filename}".encode())
        response = sock.recv(SIZE)

        if response.startswith(b"Upload Failed"):
            print(response.decode())
            is_busy = False
            return

        if response == b"READY":
            print("Upload Started : Uploading file...")

            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(SIZE)
                    if not chunk:
                        break
                    sock.send(chunk)

            sock.send(b"__EOF__")

            print(sock.recv(SIZE).decode())

        is_busy = False

    except:
        is_busy = False
        print("Upload Failed : Connection lost")


def download(sock, filename):
    global is_busy

    if os.path.exists(filename):
        print("Download Failed : File already exists")
        return

    try:
        is_busy = True

        sock.send(f"/download {filename}".encode())
        response = sock.recv(SIZE)

        if response.startswith(b"Download Failed"):
            print(response.decode())
            is_busy = False
            return

        if response == b"READY":
            print("Download Started : Downloading file...")

            with open(filename, "wb") as f:
                while True:
                    chunk = sock.recv(SIZE)
                    if b"__EOF__" in chunk:
                        chunk = chunk.replace(b"__EOF__", b"")
                        f.write(chunk)
                        break
                    f.write(chunk)

            print("Download Completed : File downloaded successfully")

        is_busy = False

    except:
        is_busy = False
        print("Download Failed : Connection lost")


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))

    print("Connected to server.")

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    while True:
        msg = input(">> ")

        if msg.startswith("/upload"):
            parts = msg.split(" ", 1)
            if len(parts) < 2:
                print("Upload Failed : Invalid command")
                continue
            upload(sock, parts[1])

        elif msg.startswith("/download"):
            parts = msg.split(" ", 1)
            if len(parts) < 2:
                print("Download Failed : Invalid command")
                continue
            download(sock, parts[1])

        else:
            sock.send(msg.encode())


if __name__ == "__main__":
    main()