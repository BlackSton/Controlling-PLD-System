import socket
from _thread import *
from threading import Thread
import time
import requests,json

class tcp():
    def __init__(self,data):
        self.data = data
        self.close  = False
        self.laser_controller = laser_tcp()
        s_log = Thread(target = self.log)
        s_log.start()
        ss = Thread(target = self.run)
        ss.start()
    def log(self): #send device log data to smpl website
        while True:
            try:
                laser_controller_dict = {}
                laser_controller_data = self.laser_controller.data["listen_result"]
                laser_controller_dict["Temperature"] = laser_controller_data["Temperature"]
                laser_controller_dict["Humidity"] = laser_controller_data["Humidity"]
                url = "http://192.168.2.100:8000/" + "PLD Room"
                re  = requests.post(url,str(laser_controller_dict))
                json_dict = json.loads(re.content.decode('utf-8'))
            except:
                print("Log Error: Laser TCP")
            #laser line laser RS232 protocol data
            try:
                laser_dict  = {}
                laser_datas  = self.data["laser"]["listen_result"]
                for laser_data in laser_datas:
                    command,data = laser_data.split("%")
                    data = data.split("=")[-1]
                    laser_dict[command] = data
                url = "http://192.168.2.100:8000/" + "LASER"
                re  = requests.post(url,str(laser_dict))
                json_dict = json.loads(re.content.decode('utf-8'))
            except:
                print("Log Error: Laser RS232")
            #vaccum line 
            try:
                vaccum_dict = {}
                vaccum_datas = self.data["vaccum"]["listen_result"]
                for vaccum_data in vaccum_datas:
                    try:
                        command,data = vaccum_data.split(",")
                        if command[0] == "P":
                            vaccum_dict["vaccum"] = data
                    except:
                        pass
                url = "http://192.168.2.100:8000/" + "PLD1"
                re  = requests.post(url,str(vaccum_dict))
                json_dict = json.loads(re.content.decode('utf-8'))
            except:
                print("Log Error: vaccum")
            time.sleep(5)
    def run(self):
        self.HOST = '192.168.0.101'#'127.0.0.1'
        self.PORT = 9889
        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.server_socket.bind((self.HOST,self.PORT))
        self.server_socket.listen()
        print("server start")
        while True:
            try:
                client_socket,addr = self.server_socket.accept()
                start_new_thread(self.threaded,(client_socket,addr))
            except:
                break
        self.server_socket.close()
        print("server closed...")
    def threaded(self,client_socket,addr):
        print("connected by:",addr[0],':',addr[1])
        stop = [False]
        name = addr[0]+":"+str(addr[1])
        th = Thread(target = self.sendresult,args=(client_socket,name,stop,))
        th.start()
        data_buffer = ""
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    print(name,"broken")
                    break
                data = data.decode('utf-8')
                data_buffer = data_buffer + data
                try:
                    if data_buffer.index('$'):
                        commands = data_buffer.split('$')[:-1]
                        data_buffer = data_buffer.split('$')[-1]
                        for command in commands:
                            command = command.split('%')
                            if len(command) == 1:
                                if command[0] == "result":
                                    buffer = ""
                                    for device in list(self.data.keys()):
                                        buffer = buffer + str(self.data[device]['result'][name])
                                        self.data[device]['result'][name] = []
                                    client_socket.send((buffer+'$').encode('utf-8'))
                                    
                                elif command[0] == "listen":
                                    buffer = ""
                                    for device in list(self.data.keys()):
                                        temp = self.data[device]['listen_result']
                                        buffer = buffer + device + '\t'
                                        for c in temp:
                                            if c == "":
                                                continue
                                            buffer = buffer + c + '\t'
                                        buffer = buffer[:-1] +'\t'+ self.data[device]['port'] + '\n'
                                    client_socket.send((buffer+'$').encode('utf-8'))
                                else:
                                    print("received wrongtype "+command[0])
                                    client_socket.send(("command error:"+command[0]+"$").encode('utf-8'))
                            else:
                                print(command)
                                device  = command[0]
                                for c in command[1:]:
                                    c = c + '%' + name
                                    self.data[device]['command'].append(c)
                            time.sleep(0.1)
                except:
                    pass
            except ConnectionResetError as e:
                break
        stop[0] = True
        th.join()
        for device in list(self.data.keys()):
            try:
                self.data[device]['result'][name].pop()
            except:
                pass
        client_socket.close()
        print("disconnected by"+addr[0],':',addr[1])
    def sendresult(self,client_socket,name,stop):
        for device in list(self.data.keys()):
            self.data[device]['result'][name] = []
        while stop[0] == False:
            for device in list(self.data.keys()):
                #try:
                result = self.data[device]['result'][name]
                if result != []:
                    print(name,result)
                    for send_file in result:
                        client_socket.send((device+'%'+send_file[0]+"$").encode('utf-8'))
                #except:
                    #pass
                self.data[device]['result'][name] = []
            time.sleep(1)

class laser_tcp():
    def __init__(self):
        self.data = {"LASER_IP":"192.168.0.118","LASER_PORT":6900,"STATE":False,"LASER_INTERVAL":1,
                     "listen_result":{"Temperature":1,"Humidity":1}}
        self.stop = False
        self.listen_keyword = ["nstate\r","htstate\r"]
        self.last_word = '\r'
        th_c = Thread(target=self.connect)
        th_c.start()
        
    def connect(self):
        while True:
            if self.stop == False:
                self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                try:
                    self.client_socket.connect((self.data['LASER_IP'], self.data['LASER_PORT'])) 
                    self.stop = False
                    self.th_r = Thread(target=self.reading)
                    self.th_l = Thread(target=self.listen)
                    self.th_r.start()
                    self.th_l.start()
                    self.data['STATE'] = True
                    return True
                except:
                    print("connection error!")
                    return False
            time.sleep(10)
    def close(self):
        self.stop = True
        self.data['STATE'] = False
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
            for com in self.listen_keyword:
                try:
                    self.client_socket.send(com.encode('utf-8'))
                except:
                    print("sending has problem!")
                    self.data['STATE'] = False
                    self.stop = True
                time.sleep(self.data['LASER_INTERVAL']/2)
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
                    #try:
                    if   command[-2] == '$':  #Device fline

                        self.data['LASER'] = command[:-2]
                        print(self.data['LASER'])
                    elif command[-1] == '\r': #LASER line
                        for line in command[:-1].split('\r'):
                            #print(line.encode('utf-8'))
                            com = line.split('=')[0]
                            result = line.split('=')[-1]
                            if   com == 'state':
                                self.data["listen_result"]["state"] = result
                            elif com == 'HT':
                                self.data["listen_result"]["Temperature"] = result.split(',')[-1]
                                self.data["listen_result"]["Humidity"] = result.split(',')[0]
                            else:
                                self.data['listen_result']['command'] = result
                    else:                     #listen line
                        print("LASER command error: ",command)
                    buffer = buffer.split('\n')[-1] # not complete line restore
                    #except:
                    #    print("Laser receive error")
            else:
                pass 
            time.sleep(0.01)
