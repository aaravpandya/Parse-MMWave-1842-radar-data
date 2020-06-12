import serial
import time
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Capture from 1842 mmwave device.')
parser.add_argument('-c',"--config", type=str,
                    help='Specify path of config file.')


def init(path):
    configFile = path
    byteBuffer = np.zeros(2**15,dtype = 'uint8')
    byteBufferLength = 0

    # OSx
    # CommandPort = serial.Serial('/dev/tty.usbmodemR00510281', 115200)
    # Dataport = serial.Serial('/dev/tty.usbmodemR00510284', 921600)

    # Linux
    #CommandPort = serial.Serial('/dev/ttyACM0', 115200)
    #Dataport = serial.Serial('/dev/ttyACM1', 921600)
        
    # Windows
    CommandPort = serial.Serial('COM3', 115200)
    Dataport = serial.Serial('COM4', 921600)

    # ------------------------------------------------------------------

    config = [line.rstrip('\r\n') for line in open(configFile)]
    success = False

    for i in config:
        CommandPort.write((i + '\n').encode())
        time.sleep(0.03)
        response = CommandPort.read(CommandPort.in_waiting)
        #print(response)
        if "Done" in str(response) or "sensorStart" in str(response) and "ERROR" not in str(response):
            print(str(i) + "  --Success!")
            success = True
        
        else:
            print(str(i) + "  --Failed!")
        time.sleep(0.01)
    return success,CommandPort, Dataport
    

def main():
    args = parser.parse_args()

    success, CommandPort, Dataport = init(args.config)
    while success:
        try:
            buffer = Dataport.read(Dataport.in_waiting)
            with open("turtlebot.dat", 'ab') as fp:
                fp.write(buffer)
            time.sleep(0.01) 
        except KeyboardInterrupt:
            CommandPort.write(('sensorStop\n').encode())
            print("sensorStop!")
            CommandPort.close()
            Dataport.close()
            print("Port Closed!")
            #win.close()
            break

if __name__ == "__main__":
    main()