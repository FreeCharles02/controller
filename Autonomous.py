import pygame
import socket
import time
import struct
import subprocess
import re


pygame.init()
ip_address =  '127.0.0.1'

def main():
    lf,rb,rf,lb = 0, 0, 0, 0
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip_address, 9999))

   # while True: uncomment this to start the while True (infinite loop)
   # I would suggest initializing each motor value, then sending them over the socket connection
   # Look at operator.py to see what variables need to be initalized to what value
   # implement time.sleep() to stop movement for now         