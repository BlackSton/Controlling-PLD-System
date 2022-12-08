# -*- coding: utf-8 -*-
"""
Created on Mon Jan  4 15:59:46 2021

@author: rltjr
"""

from threading import Thread,active_count
from time import sleep
import socket

class tcp():
    def __init__(self,data):
        self.data = data
        self.stop = False
        self.class_value = {}
        self.listen_keyword = "nstate\r"
        self.last_word = '\r'
    def connect(self):
        self.data["STATE"].append("Laser connect to %s:%s"
                                  %(self.data['LASER_IP'],self.data['LASER_PORT']))
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.data['LASER_IP'], self.data['LASER_PORT'])) 
            self.stop = False
            self.th_r = Thread(target=self.reading)
            self.th_l = Thread(target=self.listen)
            self.th_r.start()
            self.th_l.start()
            self.data['LASER_state'] = True
            self.class_value['window'].laser_control_box.setEnabled(True)
            self.data["STATE"].append("Laser Connected")
            return True
        except:
            self.data["STATE"].append("connection fail!")
            return False
    def count(self):
        print(active_count())
    def close(self):
        self.stop = True
        self.data['LASER_state'] = False
        try:
            self.client_socket.close()
            self.th_l.join()
            self.th_r.join()
        except:
            print("server was already closed...")
            pass
        print("disconnected...")
    def send(self,command):
        try:
            self.client_socket.send((command+self.last_word).encode('utf-8'))
        except:
            pass
    def listen(self):
        while self.stop == False:
            try:
                self.client_socket.send(self.listen_keyword.encode('utf-8'))
            except:
                print("sending has problem!")
                self.data['LASER_state'] = False
                self.stop = True
                pass
            sleep(self.data['LASER_INTERVAL'])
    def reading(self,):
        buffer = ""
        while self.stop == False:
            try:
                receive = self.client_socket.recv(1024).decode('utf-8')
            except:
                print("receiving error")
            try:
                receive[0]
                buffer = buffer + receive
            except:
                self.data['LASER_state'] = False
                self.stop = True
                print("LASER_3")
                break             
            
            if len(buffer.split('\n')) != 1:
                for command in buffer.split('\n')[:-1]:
                    try:
                        if   command[-2] == '$':  #Device line
                            self.data['LASER'] = command[:-2]
                            print(self.data['LASER'])
                        elif command[-1] == '\r': #LASER line
                            for line in command[:-1].split('\r'):
                                #print(line.encode('utf-8'))
                                com = line.split('=')[0]
                                result = line.split('=')[-1]
                                if   com == 'state':
                                    self.data["device"]["laser"]["listen_t"] = result
                                elif com == 'HT':
                                    self.data["device"]["HT"]["Temperature"] = result.split(',')[-1]
                                    self.data["device"]["HT"]["Humidity"] = result.split(',')[0]
                                else:
                                    self.data['device']['laser']['command'][com] = result
                        else:                     #listen line
                            print("LASER command error: ",command)
                        buffer = buffer.split('\n')[-1] # not complete line restore
                    except:
                        print("Laser receive error")
            else:
                pass 