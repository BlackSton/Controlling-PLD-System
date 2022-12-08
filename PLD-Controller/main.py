# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 01:22:54 2020

@author: rltjr
"""

import client_server
import client_laser
from gui import gui_main

if __name__ == "__main__":
    data = {"device":{"temp"   :{"listen":[],"result":{},'port':'none'}, # Devices Data LINE
                      "vaccum" :{"listen":[],"result":{},'port':'none'},
                      "laser"  :{"listen":[],"result":{},'command':{},'port':'none'},
                      "stepper":{"listen":[],"result":{},'port':'none'},
                      "HT"     :{"Temperature":"","Humidity":""       }},
            "LASER":"", #"LASER": Received Data from LASER SERVER
        'SERVER_INTERVAL':0.5,'SERVER_state':False, #client setting
        'LASER_INTERVAL':0.2,"LASER_state":False,   #Laser  setting      
        "Microstep":24700,                                     # Total step until 1 cycle
        "stop":True,                                           #Superlatttice setting
        "STATE":[]                                             #STATE line Data
        }
    
    app = gui_main.QApplication(gui_main.sys.argv) 
    
    # Making Structure
    mainWindow = gui_main.MainClass(data) # MainClass : 말그대로 MainClass 기본 Template
    tcp_server = client_server.tcp(data)
    tcp_laser  = client_laser.tcp(data)
    
    # Synchronize line
    class_value = {'window':mainWindow,'SERVER_tcp':tcp_server,'LASER_tcp':tcp_laser}
    mainWindow.class_value = class_value
    tcp_server.class_value = class_value
    tcp_laser.class_value = class_value
    mainWindow.Sync()
    
    # Running GUI Part
    mainWindow.show()
    app.exec_()
    
    # close the connected server
    tcp_server.close()
    tcp_laser.close()
