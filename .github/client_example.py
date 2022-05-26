# File: client_example.py
# Description: Example code to show a Huzzah32 connected using Wi-Fi as a client
#              when communicating over a network socket
# Author: Chris Knowles, University of Sunderland
# Date: Jan 2019

# Imports
import network
import socket
from libs.iot_app import IoTApp
from time import sleep

sckt = ""
msg_as_bytes = ""
# Classes
class MainApp(IoTApp):
    """
    This is your custom class that is instantiated as the main app object instance,
    it inherits from the supplied IoTApp class found in the libs/iot_app.py module
    which is copied when the Huzzah32 is prepared.
    This IoTApp in turn encapsulates an instance of the ProtoRig class (which is 
    found in libs/proto_rig.py) and exposes a number of properties of this ProtoRig
    instance so you do not have to do this yourself.
    Also, the IoTApp provides an execution loop that can be started by calling the
    run() method of the IoTApp class (which is of course inherited into your custom
    app class). All you have to do is define your program by providing implementations
    of the init(), loop() and deinit() methods.
    Looping of your program can be controlled using the finished flag property of
    your custom class.
    """
    def init(self):
        """
        The init() method is designed to contain the part of the program that initialises
        app specific properties (such as sensor devices, instance variables etc.)
        """
        # The convenience method connect_to_wifi() is available in the IoTApp class, it
        # requires that you pass a 4-tuple with the SSID of Wi-Fi router, the passkey
        # associated with this SSID (or "" if this is an open router), a boolean flag
        # that controls if the connection should be made immediately and finally a time
        # in milliseconds within which the connection must be made or it will time out,
        # this wait time can be 0 or less in which case there is an indefinite wait, i.e.
        # the connection is attempt forever until either it connects or you abort the run
        # of the script, this 4-tuple is passed to the connect_to_wifi() methid through
        # the parameter named wifi_settings
        wifi_config = ("DCETLocalVOIP", "kurtisnbonnin", True, 0)  # Wait time of 0 means keep attempting
                                                      # to connect
        
        # Display an OLED message to state that connection is being attempted
        self.oled_clear()
        self.oled_text("Attempt connect", 0, 10)
        self.oled_display()

        # Once a connection has been made then the detials of how the connection was set up
        # and the resulting WLAN object instance are available in the properties:-
        #
        #       self.wifi
        #       self.ssid
        #       self.passkey
        #       self.auto_connect
        #       self.wait_time
        # 
        # These are all set within the connect_to_wifi() method (or left to their current
        # settings if no wifi_setting parameter is used
        
        
        # Make connection to the server through a network socket, remember you need to used
        # the allocated IP address of the server which will vary for everyone's Huzzah32s,
        # this must be modified accordingly (or it will not work), you supply this as a
        # normal string in the form "###.###.###.###" where the #s are the numbers in the IP
        # address, note: the port number used by the server socket is 2350 (that is common
        # for all connections)
        
        
        
        #sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sckt.connect(("192.168.0.19", 2350))
        
        
        while True:
            self.connect_to_wifi(wifi_settings=wifi_config)
            sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sckt.connect(("192.168.0.19", 2350))
            global msg_as_bytes
            msg_as_bytes = sckt.recv(16)
            msg_as_string = str(bytes(msg_as_bytes), "utf-8")
            self.oled_clear()
            self.oled_text("Server says:", 0, 10)
            self.oled_text("{0}".format(msg_as_string), 0, 20)
            self.oled_display()
            sleep(1) 
 

     
        
        
    def loop(self):
        """
        The loop() method is called after the init() method and is designed to contain
        the part of the program which continues to execute until the finished property
        is set to True
        """
        
    
    def deinit(self):
        """
        The deinit() method is called after the loop() method has finished, is designed
        to contain the part of the program that closes down and cleans up app specific
        properties, for instance shutting down sensor devices. It can also be used to
        display final information on output devices (such as the OLED FeatherWing)
        """
        # In this specific implementation the deint() method does nothing, only included
        # for completeness sake
        pass

# Program entrance function
def main():
    """
    Main function, this instantiates an instance fo your custom class (where you can
    initialise your custom class instance to how you wish your app to operate) and
    then executes the run() method to get the app running
    """
    # Instantiate an instance of the custom IoTApp class (MainApp class) with the following
    # property values:-
    #
    #   name: "Client Example", this should be a maximum of 14 characters else it is truncated
    #   has_oled_board: set to True as you are using the OLED FeatherWing
    #   finish_button: set to "C" which designates Button C on the OLED FeatherWing as the
    #                  button that sets finished property to True
    #   start_verbose: set to True and the OLED FeatherWing will display a message as it
    #                  starts up the program
    #
    app = MainApp(name="Client Example", has_oled_board=True, finish_button="C", start_verbose=True)
    
    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
