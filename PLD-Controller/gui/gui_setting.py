# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 14:09:21 2021

@author: rltjr
"""
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from time import sleep

# Setting GUI Form
form_stepper = uic.loadUiType("gui/form_stepper_detail.ui")[0]
form_laser   = uic.loadUiType("gui/form_laser_detail.ui")[0]

# Setting GUI Class
class StepperClass(QMainWindow,form_stepper):
    def __init__(self,listen) :
        super().__init__()
        #control value setting
        self.listen = listen
        self.class_value = {}
        self.setupUi(self)
        self.stepper_error_str.setText("test")
        self.hall_position_str.setText(str(self.listen['stepper']['Ratio_f']))
        self.stepper_error_str.setText(str(self.listen['stepper']['e_step']))
        self.speed_str.setText(str(self.listen['stepper']['MoveSpeed']))
        self.ratio_str.setText(str(self.listen['stepper']['Ratio_l']))
        self.coordinate_str.setText(str(self.listen['stepper']['X']))
        self.micro_step_str.setText(str(self.listen['stepper']['Microstep']))
        self.Cancel_btn.clicked.connect(self.close)
        self.OK_btn.clicked.connect(self.ok_func)
    def ok_func(self):
        self.class_value['SERVER_tcp'].send("stepper%s"+self.speed_str.text())
        self.class_value['SERVER_tcp'].send("stepper%e"+self.stepper_error_str.text())
        self.class_value['SERVER_tcp'].send("stepper%k"+self.ratio_str.text())
        self.class_value['SERVER_tcp'].send("stepper%l"+self.hall_position_str.text())
        self.class_value['SERVER_tcp'].send("stepper%x"+self.coordinate_str.text())
        self.class_value['SERVER_tcp'].send("stepper%i"+self.micro_step_str.text())
        self.class_value['SERVER_tcp'].send("stepper%Save")
        self.close()
        
class LaserClass(QMainWindow,form_laser):
    def __init__(self,listen) :
        super().__init__()
        #control value setting
        self.listen = listen
        self.class_value = {}
        self.setupUi(self)
        self.laser_mode_str.setText(str(self.listen['laser']['mode']))
        self.laser_count_str.setText(str(self.listen['laser']['count']))
        self.laser_reprate_str.setText(str(self.listen['laser']['reprate']))
        self.Cancel_btn.clicked.connect(self.close)
        self.OK_btn.clicked.connect(self.ok_func)
    def ok_func(self):
        self.class_value['LASER_tcp'].send("m"+self.laser_mode_str.text())
        sleep(0.1)
        self.class_value['LASER_tcp'].send("c"+self.laser_count_str.text())
        sleep(0.1)
        self.class_value['LASER_tcp'].send("r"+self.laser_reprate_str.text())