# Imports
import os
from time import sleep
from machine import Pin
from neopixel import NeoPixel 
from libs.iot_app import IoTApp
from machine import RTC  # Real-time clock class is in the machine module

import network
import socket

# Custom class that is instantiated and inherits from the supplied IoTApp class which is copied when the Huzzah32 is
# prepared
class MainApp(IoTApp):
    """
    AP_SSID = "DCETLocalVOIP"
    AP_PSWD = "kurtisnbonnin"
    AP_TOUT = 5000
    MQTT_ADDR = "192.168.0.14"  # Your desktop PC Wi-Fi dongle IP address
    MQTT_PORT = 1883
    """
#The init is what contains the parts of the program that initialises properties for the application
    def init(self):


# Initialise the BME680 driver instance and set what needs to be recorded, in this case humidity and temperature
        # Pin 21 is connected to the NeoPixel FeatherWing via a jumper wire
        neopixel_pin = Pin(21)
    
        # Set pin 21 to be a digital output pin that is initially off
        neopixel_pin.init(mode=Pin.OUT, pull=Pin.PULL_DOWN)

        # Instantiate a NeoPixel object using the required FeatherWing pin, the number of NeoPixels, the bytes used
        # for the colour of these NeoPixels and the timing value
        self.npm = NeoPixel(neopixel_pin, 32, bpp=3, timing=1)
     
        self.rig.btnA.irq(self.btnA_handler, trigger=Pin.IRQ_FALLING)
        self.rig.btnB.irq(self.btnB_handler, trigger=Pin.IRQ_FALLING)
        # Make sure the count is set to 0 so that it can be activated later on
        self.count = 0
        # Make sure the access period is set to 0 so that this can activated later on
        self.access_period = 0
        # Show green as the room is unoccupied
        self.npm.fill((0,1,0))
        self.npm.write()
        # Make sure the access name is empty so this can be set depending on what colour is showing
        self.access = "" 
        self.btnAaccess = False
        self.btnBaccess = False

        # Set the date and time
        self.real_time_clock = RTC()
        self.real_time_clock.datetime((2022, 02, 18, 0, 9, 30, 00, 0))
		
        self.userCode = ""
        self.userCode1 = "BB235AA"
        self.userCode2 = "CK523BB"
        
        ##------------------------------------------------------------
        wifi_config = ("DCETLocalVOIP", "kurtisnbonnin", True, 0)  # Wait time of 0 means keep attempting
        self.connect_to_wifi(wifi_settings=wifi_config)
        ip_address = self.wifi.ifconfig()[0]  # First tuple entry is IP address
        sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sckt.bind((ip_address, 2350))  # Note: passed in as 2-tuple here
        sckt.listen(5)
        client_sckt, client_ip_address = sckt.accept()  # When a client tries to connect
                                                            # then accept it, recording the
                                                            # socket created for this client
                                                            # and the client IP address
        msg_as_string = "I'm connect A!!!"
        msg_as_bytes = bytes(msg_as_string, "utf-8")
        client_sckt.send(msg_as_bytes)    
        
      
    
        ##------------------------------------------------------------
    
    def ConnectA():
   
        client_sckt, client_ip_address = sckt.accept()  # When a client tries to connect
        msg_as_string = "I'm connect B!!!"
        msg_as_bytes = bytes(msg_as_string, "utf-8")
        client_sckt.send(msg_as_bytes)    

    # Create the loop so that it continues to execute until the finished property is set to True
    def loop(self):

        self.oled_clear()

        # Display the current date and time taken from the RTC instance
        now = self.real_time_clock.datetime()
        
        year = now[0]
        month = now[1]
        day = now[2]
        hour = now[4]
        minute = now[5]
        second = now[6]
        
        # Format strings to hold the current date and the current time
        datetime = "{0}/{1}/{2}|{3}:{4}:{5}".format(day, month, year, hour, minute, second)
        
        if self.access_period == 1:
            self.count += 1
            if self.count < 1:
                # Set all NeoPixels to green (0, 10, 0) colour
                self.npm.fill((0, 1, 0))  # Muted green
                self.npm.write()
            elif self.count >= 0:
                # Set all NeoPixels to red (10, 0, 0) colour
                self.npm.fill((1, 0, 0))               
                self.npm.write()
                
        # Display the current date and time on the OLED screen
        self.oled_text(self.userCode, 0, 0)
        self.oled_text(datetime, 0, 10, 20)
        self.oled_text("Count:{0}".format(self.count), 0,20)
        self.oled_display() 

        
        #Take readings every second or so
        sleep(1)

#Switches off all the NeoPixels, just to keep on top of the program itself
    def deinit(self):
        self.npm.fill((0, 0, 0))
        self.npm.write()
        pass
     
#Handler for when button A is pressed
#Makes sure that the access period is set to one and that when A is pressed then the oleds will show green
    def btnA_handler(self, pin):    
        if self.btnAaccess == True:
            self.btnAaccess = False
            self.userCode = ""
            self.access_period = 0
            self.count = 0
            self.npm.fill((0,1,0))
            self.npm.write()
            
            
            ConnectA()
            #msg_as_string = "Access 1!!!"
            #msg_as_bytes = bytes(msg_as_string, "utf-8")
            #client_sckt.send(msg_as_bytes)

        elif self.btnBaccess == True:
            return

        elif self.btnAaccess== False:
            self.btnAaccess = True
            self.userCode = self.userCode1
            self.npm.fill((1, 0, 0))
            self.access_period = 1
            
            
            client_sckt, client_ip_address = sckt.accept()  # When a client tries to connect
            msg_as_string = "I'm connect B!!!"
            
            self.npm.fill((0,1,0))
            self.npm.write()
            
            msg_as_bytes = bytes(msg_as_string, "utf-8")
            client_sckt.send(msg_as_bytes) 
            ConnectA()
            #msg_as_string = "Access 1!!!"
            #msg_as_bytes = bytes(msg_as_string, "utf-8")
            #client_sckt.send(msg_as_bytes)
                                                                   
            
                
    def btnB_handler(self, pin):

        if self.btnBaccess == True:
            self.btnBaccess = False
            self.userCode = ""
            self.access_period = 0
            self.count = 0
            self.npm.fill((0,1,0))
            self.npm.write()

        elif self.btnAaccess == True:
            return

        elif self.btnBaccess == False:
            self.btnBaccess = True
            self.userCode = self.userCode2
            self.npm.fill((1, 0, 0))
            self.access_period = 1
        
		

#Gets the name of all the files which are in the current directory on the Huzzah32's file system
#And uses the os.listdir () function
    def file_exists(self, file_name):

        file_names = os.listdir()
# Returns True if the file name is in the files list, if not then returns False
        return file_name in file_names

# Program entrance function
#States that by pressing the C button handler then this will stop the application
def main():

    app = MainApp(name="Ass1", has_oled_board=True, finish_button="C", start_verbose=True)
	
    # Run the application
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()










