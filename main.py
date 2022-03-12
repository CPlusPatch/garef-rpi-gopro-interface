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

class GoPro:
    def __init__(self, interface, quality = False):
        self.interface = interface
        self.ip = GoProCamera.GoPro.getWebcamIP(interface) # Usually IP 172.29.190.51
        self.quality = quality
        
        self.gopro = GoProCamera.GoPro(ip_address=self.ip, camera=constants.gpcontrol, webcam_device=interface, api_type=constants.ApiServerType.OPENGOPRO)
        try:
            self.gopro.setWiredControl(constants.on)
        except exceptions.WiredControlAlreadyEstablished: # Sometimes throws error 500 when control is already working, so ignore that
            pass
    
    def debug_info(self):
        debug =self.gopro.infoCamera()
        mac = ':'.join(debug['ap_mac'][i:i+2] for i in range(0,12,2))
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
            command = input("[-] Enter command (type 'help' for help): ")
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
        print("[-] Goodbye!")
        exit(0)
    
    def save_photo(self):
        print()
        name = f"photo_{time.time()}.jpg"
        self.gopro.downloadLastMedia(self.gopro.take_photo(), custom_filename=f"images/{name}")
        
        # Compress images when saving them to disk
        picture = Image.open("images/" + name)
        oldSize = os.path.getsize(os.getcwd() + "/images/" + name)
        picture.save("images/" + name, optimize=True, quality=self.quality)
        size = os.path.getsize(os.getcwd() + "/images/" + name)
        print("Compressing...")
        print(f"{round(oldSize / 1000000, 3)} Mb -> {round(size / 1000000, 3)} Mb ({round(size * 100 / oldSize, 1)}%)")
        
        print(f"Image saved to /images as {name}!")
        print()

if __name__ == "__main__":
    with open("assets/logo.txt", "r") as logo:
        print(logo.read())
    gopro = GoPro("eth1", 70)
    gopro.live_control()