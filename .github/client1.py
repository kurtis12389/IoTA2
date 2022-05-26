# File: Assignment1.py
# Description: Record air data via Huzzar32.
# Author: Kurtis Parkin
# Date: March 2022

# Imports
import os
import time
from machine import Pin
from libs.iot_app import IoTApp
from neopixel import NeoPixel
from time import sleep, sleep_ms
from libs.bme680 import BME680, OS_2X, OS_4X, OS_8X, FILTER_SIZE_3, ENABLE_GAS_MEAS
import network
import socket
from libs.iot_app import IoTApp
from libs.veml6070 import VEML6070
Flag = False    #Setting my global variables for use through my program.
x = 0
# Classes
class MainApp(IoTApp):
    def init(self):
#BME initialise with addesses and inital settings.
        self.sensor_bme680 = BME680(i2c=self.rig.i2c_adapter, i2c_addr = 0x76)
        self.sensor_bme680.set_humidity_oversample(OS_2X)
        self.sensor_bme680.set_pressure_oversample(OS_4X)
        self.sensor_bme680.set_temperature_oversample(OS_8X)
        self.sensor_bme680.set_filter(FILTER_SIZE_3)
        self.sensor_bme680.set_gas_heater_temperature(320)
        self.sensor_bme680.set_gas_heater_duration(150)
        self.sensor_bme680.select_gas_heater_profile(0)

#Timestamp Initialise
        self.rtc.datetime((2022, 02, 18, 0, 21, 30, 0, 0))

#FeatherWing Initialise
        self.neopixel_pin = self.rig.PIN_21
        self.neopixel_pin.init(mode=Pin.OUT, pull=Pin.PULL_DOWN)
        self.npm = NeoPixel(self.neopixel_pin, 32, bpp=3, timing=1)
        self.npm.fill((0, 0, 0)) #Resetting the display incase any residual code in mem.
        self.npm.write()
        
#Wifi Initialise
        wifi_config = ("DCETLocalVOIP", "kurtisnbonnin", True, 0) #Network info
        self.connect_to_wifi(wifi_settings=wifi_config) #Connection request
        sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sckt.connect(("192.168.0.19", 2350)) #Ip attempting to communicate with
           
#Receving Message        
        msg_as_bytes = sckt.recv(16)  # This blocks until message is received 
        msg_as_string = str(bytes(msg_as_bytes), "utf-8")
        
        if msg_as_string == "a":
            self.oled_text("A", 0, 0)
        elif msg_as_string == "b":
            self.oled_text("B", 0, 0)
        else:
            self.oled_text("Unknown", 0, 0)
        sleep(1)

    def loop(self):
        
        
        self.oled_clear() #Clearing OLED
        if self.sensor_bme680.get_sensor_data():
            tm_reading = self.sensor_bme680.data.temperature  # In degrees Celsius
            rh_reading = self.sensor_bme680.data.humidity     # As a percentage (ie. relative humidity)

            output1 = "{0:.2f}c, {1:.2f}%rh".format(tm_reading, rh_reading)
            self.oled_text(output1, 0, 0) #Getting data and providing it to OLED mem

            # Current date and time taken from the real-time clock
            now = self.rtc.datetime()
            year = now[0]
            month = now[1]
            day = now[2]
            hour = now[4]
            minute = now[5]
            second = now[6]
            # Format timestamp
            timestamp = "{0}-{1}-{2}|{3}:{4}:{5}".format(year, month, day, hour, minute, second)
            self.oled_text(timestamp[2:], 0, 20)
        
        message = ("Access="+str(Flag)) #Displaying the access period flag.
        self.oled_text(message, 0, 10)
        self.oled_display()
        
        if Flag == True:    #If button a is pressed then start logging data
            global x
            x += 1
            line_output = (timestamp + "|: " + output1 + "\n") #Creating the line to save
            self.file.write(line_output)    #saving the line to file
            self.oled_text(str(x), 100, 10) #Displaying the number of seconds the access period is at
            self.oled_display()

            if x < 11:      #Logic for dispalying colour depending on time on feather wing.
                self.npm.fill((0, 10, 0))
                self.npm.write()
            else:
                self.npm.fill((10, 0, 0))
                self.npm.write()
        sleep(1)
        
    def deinit(self):
        """
        The deinit() method is called after the loop() method has finished, is designed
        to contain the part of the program that closes down and cleans up app specific
        properties, for instance shutting down sensor devices. It can also be used to
        display final information on output devices (such as the OLED FeatherWing)
        """
        # Make sure the file is closed, if it exists
        if self.file:
            self.file.close()

        self.npm.fill((0, 0, 0)) #Reset wing on termination
        self.npm.write()

    def btnA_handler(self, pin):
        """
        This method overrides the inherited btnA_handler method which is provided by
        the inherited IoTApp class, you do not need to set up the pin used for the
        OLED FeatherWing button as this is done in the IoTApp class already for you
        """
        global Flag     #Setting the Access Period Flag
        if Flag != True:
            #File Writing Initialise| Checking for duplicate filenames and new file name generating.
            i = 0
            while self.file_exists("AccessPeriod_" + str(i) + ".csv"):
                i += 1
            self.file = open("AccessPeriod_" + str(i) + ".csv", "w")
            Flag = True

    def btnB_handler(self, pin):
        """
        This method overrides the inherited btnB_handler method which is provided by
        the inherited IoTApp class, you do not need to set up the pin used for the
        OLED FeatherWing button as this is done in the IoTApp class already for you
        """
        global x
        global Flag     #Setting the Access Period Flag
        if Flag != False:
            Flag = False

            end_meta=("Access Period Length: " + str(x) + " Seconds")
            self.file.write(end_meta)

            self.npm.fill((0, 0, 0)) #Reset wing on termination
            self.npm.write()
            x = 0

    def file_exists(self, file_name):
        """
        Returns True if the file (does not work with directories) with the supplied name
        exists in the current directory, otherwise returns False
        """
        # Get the name of all files in the current directory on the Huzzah32's file system
        # using the os.listdir() function
        file_names = os.listdir()

        # Return True if supplied file name is in the files list, otherwise return False
        return file_name in file_names

# Program entrance function
def main():
    """
    Main function, this instantiates an instance fo your custom class (where you can
    initialise your custom class instance to how you wish your app to operate) and
    then executes the run() method to get the app running
    """
    app = MainApp(name="ASS ONE", has_oled_board=True, finish_button="C", start_verbose=True)

    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
