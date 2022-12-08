# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 01:21:42 2020

@author: rltjr
"""
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
from time import sleep
from math import pi,sin,cos

# Import Child gui moudule
from gui import gui_connect
from gui import gui_sl
from gui import gui_setting

#main GUI Form
form_main = uic.loadUiType("gui/form_main.ui")[0]
        
#main GUI Class
class MainClass(QMainWindow, form_main):
    def __init__(self,data):
        #initial setting
        super().__init__()
        self.menu_bar() #Make menu Bar
        self.login_SERVER = gui_connect.ConnectClass(data,"SERVER")
        self.login_LASER  = gui_connect.ConnectClass(data,"LASER" )
        self.blink_number = 0 # for the receive state
        self.listen = {"temp":{},"vaccum":{},"laser":{},"stepper":{}}
        self.class_value = {}
        self.data = data
        self.setupUi(self)
        
        #Timer Setting
        self.timer = QTimer(self)
        self.timer.start(100) #check time:0.1s
        self.timer.timeout.connect(self.check)
        
        #dial#
        self.dial_stop = False
        self.dial_midpoint = (self.dial.x()+(self.dial.width()-1)/2,
                              self.dial.y()+(self.dial.height()-1)/2)
        self.dial_radius = ((self.dial.width()-1)/2)/1.8
        self.target_lenght = (self.target1.width())

        
        self.vaccum_box.setEnabled(False)
        self.stepper_main_box.setEnabled(False)
        self.temp_box.setEnabled(False)
        self.laser_box.setEnabled(False)
        #vaccum line
        self.vaccum_on.clicked.connect(self.vaccum_switch_on)
        self.vaccum_off.clicked.connect(self.vaccum_switch_off)
        #stepper line
        self.move_btn.clicked.connect(self.movefunc) 
        self.swap_stop.clicked.connect(self.s_stop)     #just   stop swap
        self.stop_btn.clicked.connect(self.stopfunc)    #forced stop
        self.zeroing_btn.clicked.connect(self.zerofunc) #zeroing
        self.Move_1.clicked.connect(self.Move_number)
        self.Move_2.clicked.connect(self.Move_number)
        self.Move_3.clicked.connect(self.Move_number)
        self.Move_4.clicked.connect(self.Move_number)
        self.stepper_setting_btn.clicked.connect(self.stepper_setting_func)
        #temp line
        self.stack = 0
        #laser line
        self.laser_on.clicked.connect(self.LASER_ON)
        self.laser_off.clicked.connect(self.LASER_OFF)
        self.laser_setting.clicked.connect(self.LASER_SETTING)
        for i in range(30):
            self.PID_str.insertItem(0,"x")
        self.PID_str.setCurrentIndex(0)
        self.PID_str.currentIndexChanged.connect(self.PatternChanged)
        self.temp_run.clicked.connect(self.temprun)
        self.temp_reset.clicked.connect(self.tempreset)
    def Sync(self):
        a = gui_sl.SLClass(self.listen,self.data)
        a.class_value = self.class_value
        self.class_value['slgui'] = a
    #   menu bar Line  #
    def menu_bar(self):
        server_connect = QAction('Server',self)
        server_connect.triggered.connect(self.connect_SERVER)
        laser_connect  = QAction('LASER',self)
        laser_connect.triggered.connect(self.connect_LASER)
        sl_connect = QAction('Setting',self)
        sl_connect.triggered.connect(self.connect_SL_menu)
        self.statusBar() #Maake StatusBar line
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        connect_menu = menubar.addMenu('&Connect')
        connect_menu.addAction(server_connect)
        connect_menu.addAction(laser_connect)
        SL_menu = menubar.addMenu('&Superlattices')
        SL_menu.addAction(sl_connect)
    def connect_SERVER(self):
        self.login_SERVER.class_value = self.class_value
        self.login_SERVER.show()
    def connect_LASER(self):
        self.login_LASER.class_value = self.class_value
        self.login_LASER.show()
    def connect_SL_menu(self):
        self.class_value['slgui'].show()


###############################################################################
#########################function line#########################################
###############################################################################
    #stepper func line#
    def movefunc(self):
        if self.mode_move.isChecked():
            self.data["STATE"].append("Moving %s step"%self.move_value.text())
            self.class_value['SERVER_tcp'].send('stepper%'+'m'+self.move_value.text())
        elif self.mode_set.isChecked() :
            self.data["STATE"].append("Moving %s step"%self.move_value.text())
            self.class_value['SERVER_tcp'].send('stepper%'+'m'+self.move_value.text())
        elif self.mode_swap.isChecked() :
            self.data["STATE"].append("Tilting ON. Step:%s"%self.move_value.text())
            self.class_value['SERVER_tcp'].send('stepper%'+'r'+self.move_value.text())
        elif self.error.isChecked():
            self.class_value['SERVER_tcp'].send('stepper%'+'e'+self.move_value.text())
        elif self.speed.isChecked():
            self.class_value['SERVER_tcp'].send('stepper%'+'s'+self.move_value.text())
        elif self.speed_2.isChecked():
            self.class_value['SERVER_tcp'].send('stepper%'+'k'+self.move_value.text())
        
    def Move_number(self):
        if   self.Move_1.isChecked():
            self.data["STATE"].append("Move to position 1")
            m = 0
            self.Move_1.toggle()
        elif self.Move_2.isChecked():
            self.data["STATE"].append("Move to position 2")
            m = self.data['Microstep']/4
            self.Move_2.toggle()
        elif self.Move_3.isChecked():
            self.data["STATE"].append("Move to position 3")
            m = 2*self.data['Microstep']/4
            self.Move_3.toggle()
        elif self.Move_4.isChecked():
            self.data["STATE"].append("Move to position 4")
            m = 3*self.data['Microstep']/4
            self.Move_4.toggle()
        mm =  m - self.coordinate
        if mm>=0:
            self.class_value['SERVER_tcp'].send('stepper%'+'m'+str(mm))
        else:
            mm = mm + self.data['Microstep']
            self.class_value['SERVER_tcp'].send('stepper%'+'m'+str(mm))
    def zerofunc(self):
        self.class_value['SERVER_tcp'].send('stepper%'+'t'+str(1))
        sleep(0.1)
        position = (self.data['Microstep']/4) *(1+(self.coordinate-self.data['Microstep']/8) // (self.data['Microstep']/4)) 
        self.data["STATE"].append("Zeroing Completed...")
        self.class_value['SERVER_tcp'].send('stepper%x'+str(position))
        
    def s_stop(self):
        self.data["STATE"].append("Tilting is stopping...")
        self.class_value['SERVER_tcp'].send('stepper%Sstop')
    def stopfunc(self):
        self.data["STATE"].append("Moving is stopped...")
        self.class_value['SERVER_tcp'].send('stepper%Stop')
    def stepper_setting_func(self):
        self.stepper_setting = gui_setting.StepperClass(self.listen)
        self.stepper_setting.class_value = self.class_value
        self.stepper_setting.show()
    #stepper func line#
    #vaccum  func line#
    def vaccum_switch_on(self):
        self.class_value['SERVER_tcp'].send("vaccum%SEN,2")
    def vaccum_switch_off(self):
        self.class_value['SERVER_tcp'].send("vaccum%SEN,1")
    #vaccum func line#
    
    
    #temp func line#
    def PatternChanged(self):
        self.PID_str.currentText()
        if self.PID_str.currentText() == "x":
            if self.PID_str.itemText(0) != 'x':
                self.PID_str.setCurrentIndex(0)
        else:
            pattern = self.PID_str.currentIndex() + 1
            self.class_value['SERVER_tcp'].send("temp%01DWR,01,0100,"+'%04i'%(pattern))
        #self.PID_str.setCurrentIndex(1) #원하는 인덱스로 밑에 갈수록 높은값.
    def temprun(self):
        self.class_value['SERVER_tcp'].send("temp%01DWR,01,0101,0001")
    def tempreset(self):
        self.class_value['SERVER_tcp'].send("temp%01DWR,01,0101,0004")
    #temp func line#
    
    
    #laser func line#
    def LASER_ON(self):
        self.class_value['LASER_tcp'].send("shot")
    def LASER_OFF(self):
        self.class_value['LASER_tcp'].send("stop")
    def LASER_SETTING(self):
        self.laser_setting = gui_setting.LaserClass(self.listen)
        self.laser_setting.class_value = self.class_value
        self.laser_setting.show()
    #laser func line#
    
###############################################################################
#########################checking line#########################################
###############################################################################
    def check_dial(self):
        try:
            targets = [self.target1,self.target2,self.target3,self.target4]
            numbering = 0
            for target in targets:
                degree = pi*(2*self.coordinate/(self.data['Microstep'])-numbering/2 + 1)
                target.move(int(self.dial_radius*cos(degree)+self.dial_midpoint[0]-self.target_lenght/2),
                            int(self.dial_radius*sin(degree)+self.dial_midpoint[1]-self.target_lenght/2))
                numbering = numbering + 1
        except:
            pass
        #main system line
    def check(self):
        # update line
        self.stepper_main_box.update()
        self.laser_box.update()
        self.temp_box.update()
        self.vaccum_box.update()
        self.groupBox_2.update()
        #dial line
        self.check_dial()
        #superlattice line
        if self.data['LASER_state' ] == True and self.data['SERVER_state' ] == True:
            self.class_value['slgui'].SL_Box.setEnabled(True)
            if self.data["stop"] == True:
                self.class_value['slgui'].SL_Start.setEnabled(True)
                self.class_value['slgui'].SL_Stop.setEnabled(False)
            else:
                #if SL started...
                self.stepper_control_box.setEnabled(False)
                self.stepper_box.setEnabled(False)
                self.laser_control_box.setEnabled(False)
                self.temp_control_box.setEnabled(False)
                self.class_value['slgui'].SL_Start.setEnabled(False)
                self.class_value['slgui'].SL_Stop.setEnabled(True)
        else:
            self.class_value['slgui'].SL_Box.setEnabled(False)
            self.class_value['slgui'].SL_Start.setEnabled(False)
            self.class_value['slgui'].SL_Stop.setEnabled(False)
            
        # State line check
        Temp = self.data["STATE"]
        self.data["STATE"] = []
        for text in Temp:
            self.STATE_str.append(text)
        # State blink line
        if self.blink_number == 0:
            self.state_LED.setText("O")
            self.blink_number += 1
        else:
            self.state_LED.setText("")
            self.blink_number =0
        if self.data['SERVER_state'] == False:
            self.server_state.setText("OFF")
        else:
            self.server_state.setText("ON")
        if self.data['LASER_state' ] == False:
            self.laser_state.setText("OFF")
        else:
            self.laser_state.setText("ON")
        #     print("server is down..")
        #     print("connecting server...")
        #     while True:   
        #         if self.class_value['SERVER_tcp'].connect():
        #             print("reconnected!")
        #         else:
        #             print("connection fail! reconnecting...")
        #         sleep(5)
        #vaccum line
        if self.data['device']['vaccum']['port'] != 'none':
            self.vaccum_box.setEnabled(True)
            try:
                vaccum_data = self.data['device']['vaccum']['listen'][0].split('%')[-1].split(',')
                pressure = vaccum_data[-1]
                state = vaccum_data[0]
                if state == "0":
                    state = "ON"
                    self.vaccum_on.setChecked(True)
                elif state == "1":
                    state = "UNDERRANGE"
                elif state == "2":
                    state = "OVERRANGE"
                elif state == "3":
                    state = "SENSOR ERROR"
                elif state == "4":
                    state = "OFF"
                    self.vaccum_off.setChecked(True)
                elif state == "5":
                    state  = "NO SENSOR"
                else:
                    state = "IDENTIFICATION ERRROR"
                self.vaccum_value.setText(pressure)
                self.vaccum_state.setText(state)
            except:
                pass
                print("waiting for connecting of vaccum")
        else:
            self.vaccum_box.setEnabled(False)
        #stepper line
        if self.data['device']['stepper']['port'] != 'none':
            self.stepper_main_box.setEnabled(True)
            try:
                for commands in self.data['device']['stepper']['listen']:
                    try:
                        command_name,command = commands.split('%')[-1].split('=')
                        self.listen['stepper'][command_name] = command
                    except:
                        print("stepper",commands)
                        pass
                ##state line(if stop is true we shut down command line)
                s_data = self.listen['stepper']['state'].split(',')
                self.listen['stepper']['X'] = int(s_data[0])
                self.listen['stepper']['MoveSpeed'] = int(s_data[1])
                self.listen['stepper']['Ratio_l'] = int(s_data[2])
                self.listen['stepper']['Ratio_f'] = int(s_data[3])
                self.listen['stepper']['e_step'] = int(s_data[4])
                self.listen['stepper']['stop'] = int(s_data[5])
                self.listen['stepper']['Microstep'] = int(s_data[6])
                self.stepper_box.setEnabled(self.listen['stepper']['stop'])
                ##coordinate
                self.data['Microstep'] = self.listen['stepper']['Microstep']
                self.coordinate = self.listen['stepper']['X'] % (self.data['Microstep'])
                #dial controller
                degree = round(360*((self.coordinate%self.data['Microstep'])/self.data['Microstep']),1)
                self.step_value.setText(str(degree)+'°')
                
            except:
                print("waiting for connecting of stepper")
            
            
        else:
            self.stepper_main_box.setEnabled(False)
        #LASER line
        #laser rs232 line
        if self.data['device']['laser']['port'] != 'none':
            
            self.LASER_BOX.setEnabled(True)
            self.laser_box.setEnabled(True)
            
            laser_datas_rs = self.data['device']['laser']['listen']
            for laser_data in laser_datas_rs:
                laser_command,laser_value = laser_data.split('?')[0],laser_data.split('=')[-1]
                self.listen['laser'][laser_command]   = laser_value
            self.LASER_OPMODE_TEXT.setText(self.listen['laser']["OPMODE"])
            self.LASER_TRIGGER_TEXT.setText(self.listen['laser']["TRIGGER"])
            self.LASER_MODE_TEXT.setText(self.listen['laser']["MODE"])
            self.LASER_COUNTS_TEXT.setText(self.listen['laser']["COUNTS"])
            self.LASER_ENERGY_TEXT.setText(self.listen['laser']["EGY"])
            self.LASER_PRESSURE_TEXT.setText(self.listen['laser']["PRESSURE"])
            self.LASER_COUNTER_TEXT.setText(self.listen['laser']["COUNTER"])
            self.LASER_REPRATE_TEXT.setText(self.listen['laser']["REPRATE"])
            self.LASER_HV_TEXT.setText(self.listen['laser']["HV"])
        else:
            if self.data['device']['laser']['port'] == 'none' and self.data['LASER_state' ] == False:
                self.laser_box.setEnabled(False)
            self.LASER_BOX.setEnabled(False)
        
        #laser tcp line
        if self.data['LASER_state' ] == True:
            
            self.TRIGGER_BOX.setEnabled(True)
            self.laser_box.setEnabled(True)
            
            try:
                laser_datas = self.data['device']['laser']['listen_t']
                laser_datas = laser_datas.split(",")
                self.listen['laser']["count"]   = laser_datas[0]
                self.listen['laser']["count_n"] = laser_datas[1]
                self.listen['laser']["reprate"] = laser_datas[2]
                self.listen['laser']["mode"]    = int(laser_datas[3])
                self.listen['laser']["state"]   = int(laser_datas[4])
                if self.listen['laser']["state"]:
                    self.LASER_STATE.setText("ON")
                else:
                    self.LASER_STATE.setText("OFF")
                if self.listen['laser']["mode"] == 1:
                    self.LASER_MODE.setText("Sync")
                else:
                    self.LASER_MODE.setText("No Sync")
                self.LASER_COUNTS.setText(self.listen['laser']["count"])
                self.LASER_COUNTER.setText(self.listen['laser']["count_n"])
                self.LASER_REPRATE.setText(self.listen['laser']["reprate"])
            except:
                pass
        else:
            if self.data['device']['laser']['port'] == 'none' and self.data['LASER_state' ] == False:
                self.laser_box.setEnabled(False)
            self.TRIGGER_BOX.setEnabled(False)


        #Temp line
        if self.data['device']['temp']['port'] != 'none':
            try:
                self.temp_box.setEnabled(True)
                temp_datas = self.data['device']['temp']['listen']
                for temp_data in temp_datas:
                    try:
                        command_names,commands = temp_data.split('%')
                        if command_names[:5] == "01DRR":
                            command_names = command_names.split(',')[2:]
                            commands      = commands.split(',')[2:]
                            for i in range(len(command_names)):
                                if int(commands[i],16) == 63536:
                                    command = -2000
                                else:
                                    command = int(commands[i],16)
                                self.listen['temp'][str(int(command_names[i]))] = command
                        else:
                            command_number,command_name = command_names.split(',')[1:3]
                            commands                    = commands.split(',')[2:]
                            for i in range(int(command_number)):
                                if int(commands[i],16) == 63536:
                                    command = -2000
                                else:
                                    command = int(commands[i],16)
                                self.listen['temp'][str(int(command_name)+i)] = command
                    except:
                        pass
                self.PV_value.setText(str(self.listen['temp']['1']/10))
                self.SV_value.setText(str(self.listen['temp']['2']/10))
                self.POWER_value.setText(str(self.listen['temp']['5']/10))
                self.PID_value.setText(str(self.listen['temp']['8']))
                # to delay for immediatly return value
                if self.PID_str.currentIndex() != self.listen['temp']['100']-1:
                    self.stack += 1
                    if self.stack > 2:
                        self.PID_str.setCurrentIndex(self.listen['temp']['100']-1)
                        self.stack = 0
                    else:
                        self.stack = 0
                if self.listen['temp']['18'] == 1:
                    self.STATE_value.setText("RESET")
                else:
                    self.STATE_value.setText("RUN")
                #switch on off line
                if self.listen['temp']['18'] == 1:
                    self.temp_reset.setEnabled(False)
                    self.temp_run.setEnabled(True)
                else:
                    self.temp_reset.setEnabled(True)
                    self.temp_run.setEnabled(False)
                #find pattern
                pattern_segment = []
                for i in range(30):
                    addr = 901 + i
                    if self.listen['temp'][str(addr)] > 0:
                        self.PID_str.setItemText(i,str(i+1))
                        pattern_segment.append(i+1)
            except:
                pass
                #print("waiting for connecting of temperature")
        else:
            self.temp_box.setEnabled(False)
        QApplication.processEvents()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        