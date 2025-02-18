import logging
import serial
import threading
import klippy

# Setup logger for logging serial interactions
logger = logging.getLogger("klipper_air_supply")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("klipper_air_supply.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class ControlAirSupply:
    def __init__(self, port='/dev/ttyACM0', baudrate=9600, timeout=1): #Serial port setting
        """Initialize serial connection and start read thread."""
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        self.buffer = []
        self.read_thread = threading.Thread(target=self.read_serial) #, args=(self.ser,))
        self.read_thread.setDaemon = True  # Make it a daemon thread so it exits when the main program exits
        self.read_thread.start()
    
    def read_serial(self):
        """Continuously read data from serial and log it."""
        line = ""
        self.buffer.clear()
        while line != "OK":
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
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
        except Exception as e:
            logger.error("Error sending command: " + str(e))

class KlipperAirControl:
    def __init__(self, config):
        
        self.air_supply = ControlAirSupply()
        self.printer_config = config.get_printer()
        self.printer = self.printer_config.lookup_object('gcode')
        self.printer.register_command("HELP_AIR", self._help, desc="Show available commands")
        self.printer.register_command("OPEN", self._open, desc="Open valve")
        self.printer.register_command("CLOSE", self._close, desc="Close valve")
        self.printer.register_command("GET_PRESSURE", self._get_pressure)
        self.printer.register_command("PULSE_MODE", self._pulse_mode, desc="Set to pulse mode")
        self.printer.register_command("SIMPLE_MODE", self._simple_mode, desc="Set to simple mode")
        self.printer.register_command("SET", self._set, desc="Set parameter")

    def _help(self, gcmd):
        self.air_supply.send_command("HELP")
    
    def _open(self, gcmd):
        self.air_supply.send_command("OPEN")
    
    def _close(self, gcmd):
        self.air_supply.send_command("CLOSE")
    
    def _get_pressure(self, gcmd):
        self.air_supply.send_command("GET_PRESSURE")
    
    def _pulse_mode(self, gcmd):
        self.air_supply.send_command("PULSE_MODE")
    
    def _simple_mode(self, gcmd):
        self.air_supply.send_command("SIMPLE_MODE")
    
    def _set(self, gcmd):
        param = gcmd.get_command_parameters()
        logger.debug(param)
        if isinstance(param, dict):
            key, value = list(param.items())[0]
            logger.debug(key, " ", value)
            formatted_command = "SET " + key.upper() + "=" + value
            logger.debug(formatted_command)
            self.air_supply.send_command(formatted_command)
        else:
            logger.error("Invalid set command format")

def load_config(config):
    return KlipperAirControl(config)
