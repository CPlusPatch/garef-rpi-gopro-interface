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
import os
import sys
import socket
from dotenv import load_dotenv
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

load_dotenv()

GOPRO_INTERFACE = os.getenv("GOPRO_INTERFACE")
GOPRO_PIN = int(os.getenv("GOPRO_PIN"))
GOPRO_IMAGE_QUALITY = int(os.getenv("IMAGE_QUALITY"))
OIC_IP = "127.0.0.1"
OIC_PORT = int(os.getenv("PORT")) # In BCM mode
# Can be "usb" or "gpio"
# USB mode: sends a shutdown order via the GoPro API
# GPIO mode: send an electric signal via GPIO to force shut down the camera
GOPRO_SHUTDOWN_MODE = "usb"
GOPRO_SMART_START = True # If True, SEND_GOPRO_ON_SIGNAL has no effect
SEND_GOPRO_ON_SIGNAL = False

assert GOPRO_SHUTDOWN_MODE in ("usb", "gpio")

class GoPro:
    def __init__(self, interface, quality = False):
        self.interface = interface
        GPIO.setup(GOPRO_PIN, GPIO.OUT)
        
        if SEND_GOPRO_ON_SIGNAL and GOPRO_SMART_START == False:
            self.turnOn()
            i = 1
            while True:
                try:
                    self.ip = GoProCamera.GoPro.getWebcamIP(interface) # Usually IP 172.29.190.51
                    break
                except:
                    print(f"[~] Connecting to camera - attempt {i}")
                    time.sleep(2)
                    i += 1
                    if i > 10:
                        raise Exception("Couldn't connect to camera (10 failed attempts)")
        
        # SMART START
        # Detects if the GoPro is on, if not turns it on
        if GOPRO_SMART_START:
            print("====== SMART START ======")
            try:
                self.ip = GoProCamera.GoPro.getWebcamIP(interface) # Usually IP 172.29.190.51
            except:
                self.turnOn()
                i = 1
                while True:
                    try:
                        self.ip = GoProCamera.GoPro.getWebcamIP(interface) # Usually IP 172.29.190.51
                        break
                    except:
                        print(f"[~] Connecting to camera - attempt {i}")
                        time.sleep(2)
                        i += 1
                        if i > 10:
                            raise Exception("Couldn't connect to camera (10 failed attempts)")
        self.quality = quality
        if GOPRO_SMART_START == False and SEND_GOPRO_ON_SIGNAL == False:
            try:
                self.ip = GoProCamera.GoPro.getWebcamIP(interface) # Usually IP 172.29.190.51
            except:
                raise Exception("Couldn't connect to camera (it is probably off)")
        
        self.gopro = GoProCamera.GoPro(ip_address=self.ip, camera=constants.gpcontrol, webcam_device=interface, api_type=constants.ApiServerType.OPENGOPRO)
        try:
            self.gopro.setWiredControl(constants.on)
        except exceptions.WiredControlAlreadyEstablished: # Sometimes throws error 500 when control is already working, so ignore that
            pass
    
    def turnOn(self):
        print("[~] Turning on GoPro... (pausing for 3s)")
        GPIO.output(GOPRO_PIN, GPIO.HIGH)
        time.sleep(3)
        GPIO.output(GOPRO_PIN, GPIO.LOW)
        print("[+] Turned on GoPro")
    
    def debug_info(self):
        """Prints all the available debug info to the terminal
        """
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
        """Turns off the connected GoPro

        Raises:
            Exception: If GPIO_SHUTDOWN_MODE isn't valid
        """
        if GOPRO_SHUTDOWN_MODE == "gpio":
            print("[~] Turning off GoPro... (pausing for 3s)")
            GPIO.output(GOPRO_PIN, GPIO.HIGH)
            time.sleep(3)
            GPIO.output(GOPRO_PIN, GPIO.LOW)
            print("[+] Turned off GoPro")
        elif GOPRO_SHUTDOWN_MODE == "usb":
            print("[-] Powering off")
            self.gopro.power_off()
        else:
            raise Exception("Invalid GOPRO_SHUTDOWN_MODE! Should one of: ['gpio', 'usb']")
        exit(0)
    
    def live_control(self):
        """Enters a "live control" mode that allow user commands to debug functions
        """
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
        """Tests ObcInterfaceClient server connection by taking an image with a connected GoPro and sending it to a server instance with an ObcInterfaceClient object
        """
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
    
    ######
    # Tests
    # OIC test: Take a photo and send it to any server instance running on localhost and same port
    # GP debug: Connect to a GoPro and enter debug mode
    ######
    main.startOicTest()
    #main.gpDebug()