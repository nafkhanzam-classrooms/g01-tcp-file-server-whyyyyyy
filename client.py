import socket
import threading
import os
import queue

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 50000
SIZE = 1024

response_queue = queue.Queue()
download_event = threading.Event()
download_info = {}


def recv_exact(sock, size):
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def receiver(sock):
    while True:
        try:
            data = sock.recv(SIZE)
            if not data:
                break

            if download_event.is_set():
                handle_download_stream(sock, data)
                continue

            if data.startswith(b"MSG:"):
                print("\n[CHAT]:", data[4:].decode())
                print(">> ", end="", flush=True)
            else:
                response_queue.put(data)

        except:
            break


def handle_download_stream(sock, first_chunk):
    filename = download_info["filename"]
    filesize = download_info["filesize"]

    received = len(first_chunk)

    with open(filename, "ab") as f:
        f.write(first_chunk)

        while received < filesize:
            chunk = sock.recv(min(SIZE, filesize - received))
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)

    print("\nDownload Completed")
    download_event.clear()
    print(">> ", end="", flush=True)


def upload(sock, filepath):
    if not os.path.exists(filepath):
        print("Upload Failed : File not found")
        return

    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    try:
        sock.send(f"/upload {filename}".encode())

        response = response_queue.get()

        if response.startswith(b"Upload Failed"):
            print(response.decode())
            return

        if response == b"READY":
            print("Uploading...")

            sock.send(filesize.to_bytes(8, 'big'))

            with open(filepath, "rb") as f:
                while chunk := f.read(SIZE):
                    sock.send(chunk)

            print(response_queue.get().decode())

    except:
        print("Upload Failed : Connection lost")


def download(sock, filename):
    if os.path.exists(filename):
        print("Download Failed : File exists")
        return

    try:
        sock.send(f"/download {filename}".encode())

        response = response_queue.get()

        if response.startswith(b"Download Failed"):
            print(response.decode())
            return

        if response == b"READY":
            sock.send(b"READY")

            filesize_data = recv_exact(sock, 8)
            filesize = int.from_bytes(filesize_data, 'big')

            download_info["filename"] = filename
            download_info["filesize"] = filesize

            open(filename, "wb").close()

            download_event.set()

            print("Downloading...")

    except:
        print("Download Failed")

def list(sock):
    try:
        sock.send("/list".encode())
        response = sock.recv(SIZE).decode()
        print("Files on server:\n", response)
    except:
        print("Failed to retrieve file list")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))

    print("Connected to server")

    threading.Thread(target=receiver, args=(sock,), daemon=True).start()

    while True:
        msg = input(">> ")

        if msg.startswith("/list"):
            parts = msg.split(" ", 1)
            if len(parts) < 1:
                print("Invalid command")
                continue
            list(sock)

        elif msg.startswith("/upload"):
            parts = msg.split(" ", 1)
            if len(parts) < 2:
                print("Invalid command")
                continue
            upload(sock, parts[1])

        elif msg.startswith("/download"):
            parts = msg.split(" ", 1)
            if len(parts) < 2:
                print("Invalid command")
                continue
            download(sock, parts[1])

        else:
            sock.send(msg.encode())


if __name__ == "__main__":
    main()