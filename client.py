import socket
import threading
import os
import time

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 50000
SIZE = 1024



def receive_messages(sock):
    while True:
        try:

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

        sock.send(f"/upload {filename}".encode())
        response = sock.recv(SIZE)

        if response.startswith(b"Upload Failed"):
            print(response.decode())
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


    except:
        print("Upload Failed : Connection lost")


def download(sock, filename):

    if os.path.exists(filename):
        print("Download Failed : File already exists")
        return

    try:

        sock.send(f"/download {filename}".encode())
        response = sock.recv(SIZE)

        if response.startswith(b"Download Failed"):
            print(response.decode())
            return

        if response == b"READY":
            print("Download Started : Downloading file...")

            data = b""

            while True:
                chunk = sock.recv(SIZE)
                if not chunk:
                    raise Exception("Connection lost")

                data += chunk

                if b"__EOF__" in data:
                    data = data.replace(b"__EOF__", b"")
                    break

            with open(filename, "wb") as f:
                f.write(data)

            print("Download Completed : File downloaded successfully")


    except Exception as e:
        print("Download Failed :", e)


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