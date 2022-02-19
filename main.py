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

class GoPro:
    def __init__(self, interface, quality = False):
        self.interface = interface
        self.ip = GoProCamera.GoPro.getWebcamIP(interface)
        self.quality = quality
        
        self.gopro = GoProCamera.GoPro(ip_address=self.ip, camera=constants.gpcontrol, webcam_device=interface, api_type=constants.ApiServerType.OPENGOPRO)
        try:
            self.gopro.setWiredControl(constants.on)
        except exceptions.WiredControlAlreadyEstablished: # Sometimes throws error 500 when control is already working, so ignore that
            pass
    
    def save_photo(self):
        name = f"photo_{time.time()}.jpg"
        self.gopro.downloadLastMedia(self.gopro.take_photo(), custom_filename="images/" + name)
        
        # Compress images when saving them to disk
        picture = Image.open("images/" + name)
        picture.save("images/" + name, optimize=True, quality=self.quality)
        
        print(f"[+] Image saved to /images as {name}!")

if __name__ == "__main__":
    with open("assets/logo.txt", "r") as logo:
        print(logo.read())
    gopro = GoPro("eth1", 70)
    gopro.save_photo()