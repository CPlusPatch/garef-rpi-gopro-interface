import socket
from PIL import Image
import time
import os
from dotenv import load_dotenv

load_dotenv()

SERVER_IP = "127.0.0.1"
SERVER_PORT = int(os.getenv("PORT"))

class Server:
    def __init__(self, ip, port): 
        print("[+] Started dev server...")
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip, self.port))
        self.socket.listen()
    
    def acceptConnection(self):
        self.conn, self.clientAddr = self.socket.accept()
        print(f"[+] Connected to {self.clientAddr}")
    
    def run(self):
        self.acceptConnection()
        data = b""
        image = b""
        while data.decode("utf-8") != "BEGIN":
            data = self.conn.recv(1024)
        print("[+] Receiving image")
        filename = f"server-images/{time.time()}.jpg"
        file = open(filename, "wb")
        data = self.conn.recv(1024)
        file.write(data[:-3]) # I have no idea why it needs -3, just keep it
        while True:
            data = self.conn.recv(1024)
            image += data
            if image[-3:] == b"END":
                file.write(data)
                break
            else:
                file.write(data)
        file.close()
        
        print("[+] Sending ACK")
        self.conn.sendall("ACK".encode("utf-8"))
            

if __name__ == "__main__":
    server = Server(SERVER_IP, SERVER_PORT)
    server.run()
    server.socket.close()