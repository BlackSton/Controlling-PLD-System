# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 13:31:33 2021

@author: rltjr
"""
from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox,QMainWindow

# Connect GUI Form
form_connect = uic.loadUiType("gui/form_connect.ui")[0]

# Connect GUI Class
class ConnectClass(QMainWindow, form_connect):
    def __init__(self,data,mode) :
        super().__init__()
        #control value setting
        self.mode = mode
        self.data = data
        self.class_value = {}
        self.setupUi(self)
        self.load_setting()
        self.ip_str.setText(self.data[self.mode+'_IP'])
        self.port_str.setText(self.data[self.mode+'_PORT'])
        self.connect_btn.clicked.connect(self.connect_server)
    def load_setting(self): #load setting.ini and load ip and port
        try:
            f = open('setting.ini','r')
        except:
            f = open('setting.ini','w')
            f.close()
            f = open('setting.ini','r')
        lines = f.readlines()
        f.close()
        for line in lines:
            if line[-1] == '\n':
                line = line[:-1]
            temp = line.split('=')
            self.data[temp[0]] = temp[1]

    def connect_server(self):
        self.data[self.mode+'_IP']=self.ip_str.text()
        self.data[self.mode+'_PORT']=int(self.port_str.text())
        if self.class_value[self.mode+'_tcp'].connect():
            f = open("setting.ini",'w')
            f.write("SERVER_IP="+self.data['SERVER_IP']+'\n')
            f.write("SERVER_PORT="+str(self.data['SERVER_PORT'])+'\n')
            f.write("LASER_IP="+self.data['LASER_IP']+'\n')
            f.write("LASER_PORT="+str(self.data['LASER_PORT'])+'\n')
            f.close()
            self.close()
        else:
            buttonReply = QMessageBox.information(
            self, 'Error', "Connection Error!", 
            QMessageBox.Yes
            )
            #if buttonReply == QMessageBox.Yes:
            #    print('Yes clicked.')
            print("connection error please reconnect!!")