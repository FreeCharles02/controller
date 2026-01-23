import struct
import socket
import time
#from serial import Serial 
#host = get_non_loopback_ip()
host = '127.0.0.1'
port = 9999

# TCP internet connection
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", port))
server.listen(1)
'''serial_port = "/dev/serial0" #serial1'
serial_port2 = "/dev/ttyAMA2"
serial_port3 = "/dev/ttyAMA3"
baudrate = 115200

roboclaw2 = Serial(serial_port2, baudrate, timeout=1)
roboclaw3 = Serial(serial_port3, baudrate, timeout=1)
roboclaw = Serial(serial_port, baudrate, timeout=1)'''


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
        
    '''  rb, rf, lb, lf = struct.unpack('!' + 'B' * 4, buf)
        roboclaw.write(bytes([rb])) #forwards 
        roboclaw.write(bytes([rf])) #stop
        roboclaw2.write(bytes([lf])) #backwards
        roboclaw2.write(bytes([lb])) #forwards '''
       

if __name__ == "__main__":
    while(True):
        try:
            main()
        except (socket.timeout,ConnectionResetError):
            time.sleep(0.1)