import socket
import sys
from time import sleep


def run(): 
    HOST, PORT = "localhost", 9931
    data = " ".join(sys.argv[1:])

    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        counter = 0
        while counter < 5:
            try:
                sock.connect((HOST, PORT))
            except ConnectionResetError as e:
                print(e)
                counter += 1
                sleep(1)
                continue
            break
        sock.sendall(bytes(data + "\n", "utf-8"))

        # Receive data from the server and shut down
        received = str(sock.recv(1024), "utf-8")

    print("Sent:     {}".format(data))
    print("Received: {}".format(received))


if __name__ == "__main__":
    run()

