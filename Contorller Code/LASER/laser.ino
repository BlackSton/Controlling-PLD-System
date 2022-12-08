#include <ESP8266WiFi.h>
#include <Ticker.h>
#include "DHT.h"

#define MAX_SRV_CLIENTS 4 //how many clients should be able to telnet to this ESP8266
#define DHTTYPE DHT22 // DHT22 (AM2302)

#define Trigger 4
#define Sync 5
#define LED  D5
#define StateLED D6
#define Tem  D4

const char* MY_WIFI_SSID = "SMPL";
const char* MY_WIF_PASSWORD = "youcandoit!!!";
String     inputString_s;
String     inputString[MAX_SRV_CLIENTS];
boolean end_value = false;
boolean stringComplete_s;
boolean stringComplete[MAX_SRV_CLIENTS];
WiFiServer server(6900);
WiFiClient serverClients[MAX_SRV_CLIENTS];
DHT dht(Tem, DHTTYPE);

int duration = 100;
int duration_s = 40;
int reprate=10;
int count   =3000;
int count_n =0;
int state = 0; //0:off,1:on
int Mode_m = 1;
boolean counting = false;



Ticker flipper;
Ticker flipper_LED;

void setup() {
  Serial.begin(9600);
  pinMode (Trigger,OUTPUT);
  pinMode (StateLED,OUTPUT);
  pinMode (LED,OUTPUT);
  pinMode (Sync,INPUT_PULLUP);
  dht.begin();
  attachInterrupt(Sync,Sync_func,FALLING);
  timer1_isr_init();
  timer1_attachInterrupt(trigger_func);
  digitalWrite (LED, HIGH);
  WiFi.begin(MY_WIFI_SSID, MY_WIF_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  server.begin();
  server.setNoDelay(true);
  digitalWrite (LED, LOW);
  flipper.attach(1/(float)reprate,trigger_func);
  flipper_LED.attach(0.5/(float)reprate,LED_func);
  //Serial.print(WiFi.localIP());
  //Serial.println("Server started");
}
//Sync Interrupt func
ICACHE_RAM_ATTR void Sync_func()
{
  if(Mode_m==1)
  {
  if(count == count_n)
  {
    end_value = 1;
    count_n = 0;
    state = 0;
  }
  if(state==1)
  {
    
    count_n = count_n + 1;
  }
  }
}
//Trigger Interrupt func
void trigger_func()
{
  if(Mode_m==2)
  { 
    if(count == count_n){
      state = 0;
      end_value = 1;
      count_n = 0;
      return;
      }
    if(state == 1){
    count_n = count_n + 1;
    }
  }
  if(state==1)
  { 
    digitalWrite (Trigger, HIGH);
    delayMicroseconds(40);
    digitalWrite (Trigger, LOW);
  }
  
}
void LED_func()
{
  if(state==1){
  digitalWrite(LED,!(digitalRead(LED)));
  }
}
void State_func()
{
  digitalWrite(StateLED,!(digitalRead(StateLED)));
}
void Temp(int i)
{
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  serverClients[i].print("HT=");
  serverClients[i].print(h);
  serverClients[i].print(',');
  serverClients[i].println(t);
  inputString[i]="";
}
void State(int i)
{
  serverClients[i].print("state=");
  serverClients[i].print(count);
  serverClients[i].print(',');
  serverClients[i].print(count_n);
  serverClients[i].print(',');
  serverClients[i].print(reprate);
  serverClients[i].print(',');
  serverClients[i].print(Mode_m);
  serverClients[i].print(',');
  serverClients[i].println(state);
  inputString[i]="";
}
void Count(int i)
{
   int test;
   inputString[i].setCharAt(0,' ');
   test=inputString[i].toInt();
   if(count > 0)
   {
    count = test;
    serverClients[i].print("Count=");
    serverClients[i].print(count);
    serverClients[i].println("$");
   }else{
    serverClients[i].print("Count Value Error!:");
    serverClients[i].print(test);
    serverClients[i].println("$");
   }
   inputString[i]="";
}
void Mode(int i)
{
   int test;
   inputString[i].setCharAt(0,' ');
   test=inputString[i].toInt();
   if(test > 0 && test <3)
   {
    Mode_m = test;
    serverClients[i].print("Mode_m=");
    serverClients[i].print(Mode_m);
    serverClients[i].println("$");
   }else{
    serverClients[i].print("Mode_m Value Error!:");
    serverClients[i].print(test);
    serverClients[i].println("$");
   }
   inputString[i]="";
}
void Reprate(int i)
{
   int test;
   inputString[i].setCharAt(0,' ');
   test=inputString[i].toInt();
   if(reprate > 0 && reprate < 41)
   {
    reprate = test;
    serverClients[i].print("Reprate=");
    serverClients[i].print(reprate);
    serverClients[i].println("$");
    flipper.attach(1/(float)reprate,trigger_func);
    flipper_LED.attach(0.5/(float)reprate,LED_func);
   }else{
    serverClients[i].print("Count Value Error!:");
    serverClients[i].print(test);
    serverClients[i].println("$");
   }
   inputString[i]="";
}
void loop() {
  if(state==0){
  digitalWrite(LED,false);
  }
  uint8_t i;
  //check if there are any new upcoming clients
  if (server.hasClient()){
  for(i = 0; i < MAX_SRV_CLIENTS; i++){
  //find those free/disconnected spot
   if (!serverClients[i] || !serverClients[i].connected()){
  if(serverClients[i]) serverClients[i].stop();
  serverClients[i] = server.available();
  //Serial.print("New client: "); Serial.print(i);
  continue;
   }
  }
  
  //no free/disconnected spot so reject
  WiFiClient serverClient = server.available();
  serverClient.stop();
  }
  
  //check clients for data
  for(i = 0; i < MAX_SRV_CLIENTS; i++){
  if (serverClients[i] && serverClients[i].connected()){
  while(serverClients[i].available()){
    //get data from the telnet client and push it to the UART
    char inChar = (char)serverClients[i].read();
    if (inChar > 0)     {inputString[i] += inChar;}  // add it to the inputString[i]:
    if (inChar == '\r') { stringComplete[i] = true;}
  }
  }
  }

  for(i = 0; i < MAX_SRV_CLIENTS; i++){
    if (stringComplete[i]) 
    {  
      if (inputString[i].charAt(0)=='c') {Count(i);   }
      if (inputString[i].charAt(0)=='m') {Mode(i);   }
      if (inputString[i].charAt(0)=='r') {Reprate(i);   }
      if (inputString[i]=="nstate\r")    {State(i);  }
      if (inputString[i]=="htstate\r")   {Temp(i);  }
      if (inputString[i]=="shot\r")      {digitalWrite (LED, LOW);state = 1;count_n=0;serverClients[i].println("Started...$");inputString[i] = "";}
      if (inputString[i]=="stop\r")      {state = 0;serverClients[i].println("Stoped...$");digitalWrite (LED, LOW);count_n=0;inputString[i] = "";}
      if (inputString[i] !="")           {Serial.flush();Serial.print(inputString[i]);}
      inputString[i] = ""; stringComplete[i] = false; // clear the string:
      State_func();
    }
  }
  //Serial Communication Part
  while (Serial.available()) 
  {
    char inChar = (char)Serial.read();   
    if (inChar > 0)     {inputString_s += inChar;}  // add it to the inputString:
    if (inChar == '\r') {stringComplete_s = true;} // if the incoming character is a newline, set a flag so the main loop can do something about it: 
  }
  if (stringComplete_s) {
    for(i = 0; i < MAX_SRV_CLIENTS; i++)
    {
      if (serverClients[i] && serverClients[i].connected())
      {
        serverClients[i].print(inputString_s);
      }
     }
      inputString_s = "";stringComplete_s = false;
    }
    if(end_value == true){
  for(int i = 0; i < MAX_SRV_CLIENTS; i++)
      {
        if (serverClients[i] && serverClients[i].connected())
      {
        serverClients[i].println("End...$");
      }
      }
      end_value = false;
  }
  }
