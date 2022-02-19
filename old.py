import cv2
import time

class GoPro:
    def __init__(self, port: int):
        self.port = port
        self.cap = cv2.VideoCapture('udp://@:{}'.format(port), cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        if not self.cap.isOpened():
            print('VideoCapture not opened')
            exit(-1)
        print("[+] GoPro initialised on udp://{}".format(port))

    
    def take_frame(self) -> bool:
        ret, frame = self.cap.read()
        if not ret:
            return False
        cv2.imwrite('photos_famille_garef/amongus_'+ str(time.time()) +'.jpeg', frame)
        cv2.imshow('sus', frame)

        if cv2.waitKey(1)&0XFF == ord('q'):
            self.close()
            return False
        print("[+] ", end="")
        return True
    
    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()
    
    def run(self, photos: int):
        print("[DEBUG] Taking {} photos".format(photos))
        for _ in range(photos):
            self.take_frame()

if __name__ == "__main__":
    gopro = GoPro(8554)
    gopro.run(1000)
    gopro.close()
