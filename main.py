#
# GoPro-RPi Python Interface
# --------------------------
# By:        Gaspard Wierzbinski
# Date:      February 2022
# License:   MIT License
# --------------------------
#
# GAREF AEROSPATIAL 2022
#
from goprocam import GoProCamera, constants, exceptions
import time
from PIL import Image
import json
import os
import sys
import socket

GOPRO_INTERFACE = "eth1"
GOPRO_IMAGE_QUALITY = 70
OIC_IP = "127.0.0.1"
OIC_PORT = 65401

class GoPro:
    def __init__(self, interface, quality = False):
        self.interface = interface
        # Crash if the camera is not connected
        try:
            self.ip = GoProCamera.GoPro.getWebcamIP(interface) # Usually IP 172.29.190.51
        except exceptions.CameraNotConnected:
            print("[x] Camera not connected, exiting :(")
            sys.exit(0)
        self.quality = quality
        
        self.gopro = GoProCamera.GoPro(ip_address=self.ip, camera=constants.gpcontrol, webcam_device=interface, api_type=constants.ApiServerType.OPENGOPRO)
        try:
            self.gopro.setWiredControl(constants.on)
        except exceptions.WiredControlAlreadyEstablished: # Sometimes throws error 500 when control is already working, so ignore that
            pass
    
    def debug_info(self):
        debug = self.gopro.infoCamera()
        mac = ':'.join(debug['ap_mac'][i:i+2] for i in range(0,12,2)) # Formats the MAC address nicely
        print()
        print(f"MAC:               {mac.upper()}")
        print(f"SSID:              {debug['ap_ssid']}")
        print(f"Board type:        {debug['board_type']}")
        print(f"Firmware version:  {debug['firmware_version']}")
        print(f"SHA1:              {debug['git_sha1']}")
        print(f"Model name:        {debug['model_name']}")
        print(f"Serial number:     {debug['serial_number']}")
        print("Update status:     ", end="")
        if debug["update_required"] == "0":
            print("Up to date")
        else:
            print("Available")
        print()
        print(f"OS:                {sys.platform}")
        print(f"Working directory: {os.getcwd()}")
        print(f"Python version:    {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}")
        print()

    
    def power_off(self):
        print("[-] Powering off")
        self.gopro.power_off()
        exit(0)
    
    def live_control(self):
        command = ""
        while not ("stop" in command):
            command = input("[ ] Enter command (type 'help' for help):\n$ ")
            if "photo" in command:
                self.save_photo()
            elif "off" in command:
                self.power_off()
            elif "debug" in command:
                self.debug_info()
            elif "help" in command:
                with open("assets/help.txt", "r") as help:
                    print(help.read(), end="")
            elif "troll" in command:
                with open("assets/troll.txt", "r") as sus:
                    print(sus.read())
            else:
                print("[!] Invalid command")
        print("[-] Exiting live control!")
    
    def save_photo(self, optimise = True) -> str:
        """Takes an image using the GoPro and saves it to disk after (optionally) compressing it

        Args:
            optimise (bool, optional): Whether to compress the image or not (recommended). Defaults to True.

        Returns:
            str: Path of saved image on disk
        """
        print()
        name = f"photo_{time.time()}.jpg"
        self.gopro.downloadLastMedia(self.gopro.take_photo(), custom_filename=f"images/{name}")
        
        # Compress images when saving them to disk
        picture = Image.open(f"images/{name}")
        oldSize = os.path.getsize(os.getcwd() + "/images/" + name)
        picture.save(f"images/{name}", optimize=True, quality=self.quality)
        size = os.path.getsize(os.getcwd() + "/images/" + name)
        print("Compressing...")
        print(f"{round(oldSize / 1000000, 3)} Mb -> {round(size / 1000000, 3)} Mb ({round(size * 100 / oldSize, 1)}%)")
        
        print(f"Image saved to /images as {name}!")
        print()
        return os.getcwd() + "/images/" + name

class ObcInterfaceClient:
    def __init__(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip, self.port = (ip, port)
        self.connected = False
        print("[+] Initialised OBC Interface Client")
    
    def connect(self):
        print("[⠞] Waiting for server to connect...")
        try:
            self.socket.connect((self.ip, self.port))
        except ConnectionRefusedError:
            raise Exception("Connection was refused, maybe the server is offline?")
        self.connected = True
    
    def checkConnected(self):
        """Can be  used to crash the program if server connection is not established

        Raises:
            Exception: If this instance is not currently connected to a server
        """
        if not self.connected:
            raise Exception("This ObcInterfaceClient instance is not connected to server!")
    
    def send(self, data: str, bytes: bool = True):
        self.checkConnected()
        if bytes:
            self.socket.sendall(data)
        else:
            self.socket.sendall(data.encode("utf-8"))
        
    
    def receive(self, bytes: bool = True):
        self.checkConnected()
        if bytes:
            return self.socket.recv(1024)
        else:
            return self.socket.recv(1024).decode("utf-8")

class Main:
    def __init__(self, gpInterface: str, gpImageQuality: int, oicIp: str, oicPort: int):
        with open("assets/logo.txt", "r") as logo:
            print(logo.read())
        self.gopro = GoPro(gpInterface, gpImageQuality)
        self.oic = False
        self.oicIp = oicIp
        self.oicPort = oicPort
    
    def initOic(self, ip, port):
        self.oic = ObcInterfaceClient(ip, port)
        self.oic.connect()
    
    def gpDebug(self):
        self.gopro.live_control()
    
    def startOicTest(self):
        print("================== DEBUG TESTS ==================")
        if not self.oic:
            print("> INITIALISING OIC")
            self.initOic(self.oicIp, self.oicPort)
            print("> TAKING PHOTO")
        photo1 = self.gopro.save_photo()
        with open(photo1, "rb") as photo1_b:
            print("> SENDING TO OBC")
            self.oic.send("BEGIN", False)
            size = 0
            while True:
                data = photo1_b.read(1024)
                size += len(data)
                self.oic.send(data)
                if not data:
                    break
            self.oic.send("END", False)
            print("> WAITING FOR RESPONSE")
            while self.oic.receive().decode("utf-8") != "ACK":
                pass
        print("> GOT RESPONSE")
        print("> TEST SUCCESSFUL")
            

if __name__ == "__main__":
    main = Main(GOPRO_INTERFACE, GOPRO_IMAGE_QUALITY, OIC_IP, OIC_PORT)
    main.startOicTest()
    #main.gpDebug()