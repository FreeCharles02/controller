import struct
import socket
import time

#host = get_non_loopback_ip()
host = '127.0.0.1'
port = 9999

# TCP internet connection
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", port))
server.listen(1)



def main():
    print("gettin connection...")
    client, addr = server.accept()
    print("got a connection")

    # Checks constantly for client data
    while True:
      #  client.send("Hello from RaspberryPi".encode())
#        pca1.frequency = 50
        buf = ''
        start = time.time()
        while (len(buf) < 4):
            buf = client.recv(4)
            if (time.time()-start) > 1:
                return socket.timeout

        rb, rf, lb, lf = struct.unpack('!' + 'B' * 4, buf)
        print("RB: ", rb)
        print("RF: ", rf)
        print("LF: ", lf)
        print("LB: ", lb)

if __name__ == "__main__":
    while(True):
        try:
            main()
        except (socket.timeout,ConnectionResetError):
            time.sleep(0.1)