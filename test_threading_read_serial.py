import logging
import serial
import threading

# Setup logger for logging serial interactions
logger = logging.getLogger("klipper_air_supply")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("klipper_air_supply.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class ControlAirSupply:
    def __init__(self, port='COM5', baudrate=9600, timeout=1): #Serial port setting
        """Initialize serial connection and start read thread."""
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        self.buffer = []
        self.read_thread = threading.Thread(target=self.read_serial, daemon=True)
        self.read_thread.start()
    
    def read_serial(self):
        """Continuously read data from serial and log it."""
        while line != "OK":
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    logger.debug("Received: " + line)
                    self.buffer.append(line)                        
            except Exception as e:
                logger.error("Error reading serial: " + str(e))
                break
        logger.debug("Full Response:\n" + "\n".join(self.buffer))
        self.buffer.clear()

    def send_command(self, command):
        """Send command to air supply system."""
        try:
            self.ser.write((command + '\n').encode('utf-8'))
            logger.debug("Sent: " + command)
            self.read_serial()
        except Exception as e:
            logger.error("Error sending command: " + str(e))

air_supply = ControlAirSupply()
while True:
    air_supply.send_command(input("Pleas input the key : "))