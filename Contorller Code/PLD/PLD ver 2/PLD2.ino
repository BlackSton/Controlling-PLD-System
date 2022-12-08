#include <EEPROM.h>

int stop_value = 1; //stopping sequence 0:move 1:stop 2:manual
boolean swap_stop  = false;
int MoveSpeed=500; //step in Microseconds
int SwapSpeed_fast = 500;
int SwapSpeed_low = 2000; //speed in slow stepping
int error_step = 300;
int error_speed = 100;
int roller_value;
int roller_speed=800;
int Microstep = 24710;
int count = 0;
int VIR  = 0;
int VIR1 = 0;
int VIR2 = 0;
int VIR3 = 0;
int VIR4 = 0;
boolean VBt1 = false;
boolean VBt2 = false;
boolean VBt3 = false;
boolean VBt4 = false;
boolean Vm   = false; // value - manual
int Mm = 0; // manual movement state
unsigned int  X= 4000;
boolean RS = false;
String     inputString = "";       // a string to hold incoming data
boolean stringComplete = true;     // whether the string is completet

int arr[] = {X,MoveSpeed,error_step,SwapSpeed_fast,SwapSpeed_low,Microstep};


# define X_DIR_5v 12  //DIR+(+5v) axis stepper motor direction control  Brown
# define X_STP_5v 11  //PUL+(+5v) axis stepper motor step control       RED
# define X_ENB_5v 10
# define Receive 8
# define LManual 7
# define LMove 6
# define Manual 9 // Manual button
# define roller A5
# define IR1 A1
# define IR2 A2
# define IR3 A3
# define IR4 A4
# define Bt1 2
# define Bt2 3
# define Bt3 4
# define Bt4 5


void setup() {// *************************************************************     setup
for(int i=0;i <sizeof(arr)/sizeof(arr[0]);i++)
{
  byte hiByte = EEPROM.read(i*2);
  byte loByte = EEPROM.read(i*2+1);
  arr[i] = int(word(hiByte,loByte));
}
X               = arr[0];
MoveSpeed       = arr[1];
error_step      = arr[2];
SwapSpeed_fast  = arr[3];
SwapSpeed_low   = arr[4];
Microstep       = arr[5];
//pinMode (X_EN_5v ,OUTPUT); //ENA+(+5V)
pinMode (X_DIR_5v,OUTPUT); //DIR+(+5v)
pinMode (X_STP_5v,OUTPUT); //PUL+(+5v)
pinMode (X_ENB_5v,OUTPUT); //PUL+(+5v)
pinMode (Receive,OUTPUT );
pinMode (LManual,OUTPUT );
pinMode (LMove,OUTPUT );
pinMode (Manual,INPUT );
pinMode (Bt1,INPUT);
pinMode (Bt2,INPUT);
pinMode (Bt3,INPUT);
pinMode (Bt4,INPUT);
//digitalWrite (X_EN_5v , LOW); //ENA+(+5V) low=enabled
digitalWrite (X_DIR_5v, LOW); //DIR+(+5v)
digitalWrite (X_STP_5v, LOW); //PUL+(+5v)
digitalWrite (Receive, LOW);
digitalWrite (LMove, LOW);

Serial.begin(115200);
}
void State()
{
  Serial.print("state=");
  Serial.print(X);
  Serial.print(',');
  Serial.print(MoveSpeed);
  Serial.print(',');
  Serial.print(SwapSpeed_low);
  Serial.print(',');
  Serial.print(SwapSpeed_fast);
  Serial.print(',');
  Serial.print(error_step);
  Serial.print(',');
  Serial.print(stop_value);
  Serial.print(',');
  Serial.println(Microstep);
  
  inputString="";
}
void MoveX(float mm ,float ps,float rs){ // **************************************************************    Move
int xt;
float a;
if (mm == 0){
  inputString.setCharAt(0,' ');
  mm=inputString.toInt();
  Serial.print("move=");
  Serial.println(mm);
  inputString="";
}
if (mm>0)
{digitalWrite (X_DIR_5v,HIGH);xt=1;}
else
{digitalWrite (X_DIR_5v,LOW);xt=-1;}
for (int i=0; i<abs(mm); i++)
{    
      if(stop_value == 2){
      VBt1 = digitalRead(Bt1);
      VBt2 = digitalRead(Bt2);
      VBt3 = digitalRead(Bt3);
      VBt4 = digitalRead(Bt4);
      roller_value = analogRead(roller);
  
      if(VBt1 == 1 && Mm != 1){break;}
      if(VBt2 == 1 && Mm != 2){break;}
      if(VBt3 == 1 && Mm != 3){break;}
      if(VBt4 == 1 && Mm != 4){break;}
      }
     if(stop_value == 1){break;}
     if(X == Microstep*2){X = Microstep;}
     while (Serial.available()) 
        {
          char inChar = (char)Serial.read();   
          if (inChar > 0)     {inputString += inChar;}  // add it to the inputString:
          if (inChar == '\n') { stringComplete = true;} // if the incoming character is a newline, set a flag so the main loop can do something about it: 
        }
      if (stringComplete) 
       {  
        if (inputString=="nstate\n"){State(); }
        if (inputString=="Stop\n")  {stop_value = true; swap_stop =true;Serial.println("stoping.."); break;  }
        if (inputString !="") {Serial.print("BAD COMMAND="+inputString);}// Serial.print("\n"); }// "\t" tab      
        inputString = ""; stringComplete = false; // clear the string:
        if(RS == false){digitalWrite (Receive,HIGH);RS=true;}else{digitalWrite (Receive,LOW);RS=false;}
       }
     a = ps + (rs-ps)*i/abs(mm);
     digitalWrite (X_STP_5v, HIGH);
     digitalWrite (LMove, HIGH);
     delayMicroseconds(int(a));
     digitalWrite (X_STP_5v, LOW);
     digitalWrite (LMove, LOW);
     delayMicroseconds(int(a));
     X = X + xt;
}
inputString="";
}

void Swap()
{
  inputString.setCharAt(0,' ');
  int mm=inputString.toInt();
  Serial.print("swap=");
  Serial.println(mm);
  inputString="";
  MoveX(mm,SwapSpeed_low,SwapSpeed_fast);
  while(true){
    MoveX(-error_step,error_speed,error_speed);
    MoveX(-mm,SwapSpeed_fast,SwapSpeed_low);
    MoveX(-mm,SwapSpeed_low,SwapSpeed_fast);
    if(swap_stop == true){
      MoveX(mm+error_step,MoveSpeed,MoveSpeed);
      swap_stop = false;
      break;
    }
    MoveX(error_step,error_speed,error_speed);
    MoveX(mm,SwapSpeed_fast,SwapSpeed_low);
    MoveX(mm,SwapSpeed_low,SwapSpeed_fast);
  }
}
void MSwap(int mm)
{
  MoveX(mm,SwapSpeed_low,SwapSpeed_fast);
  if(roller_value < 20){MoveX((Mm-1)*Microstep/4- int(X)%Microstep,MoveSpeed,MoveSpeed);return;}
  MoveX(-error_step,error_speed,error_speed);
  if(roller_value < 20){MoveX((Mm-1)*Microstep/4- int(X)%Microstep,MoveSpeed,MoveSpeed);return;}
  MoveX(-mm,SwapSpeed_fast,SwapSpeed_low);
  if(roller_value < 20){MoveX((Mm-1)*Microstep/4- int(X)%Microstep,MoveSpeed,MoveSpeed);return;}
  MoveX(-mm,SwapSpeed_low,SwapSpeed_fast);
  if(roller_value < 20){MoveX((Mm-1)*Microstep/4- int(X)%Microstep,MoveSpeed,MoveSpeed);return;}
  MoveX(error_step,error_speed,error_speed);
  if(roller_value < 20){MoveX((Mm-1)*Microstep/4- int(X)%Microstep,MoveSpeed,MoveSpeed);return;}
  MoveX(mm,SwapSpeed_fast,SwapSpeed_low);
  if(roller_value < 20){MoveX((Mm-1)*Microstep/4- int(X)%Microstep,MoveSpeed,MoveSpeed);return;}
}
void SetX()
{
  inputString.setCharAt(0,' ');
  X = inputString.toInt();
  Serial.print("X=");
  Serial.println(X);
  inputString="";
}
void MSpeed(){  // ************************************************************   MoveSpeed
 inputString.setCharAt(0,' ');
 MoveSpeed=inputString.toInt();
 if(MoveSpeed > 60)
 {
   Serial.print("Speed=");
   Serial.println(MoveSpeed);
 }else{
   Serial.println("speed value errror!!");
 }
 inputString="";
}
void ErrorStep()
{
  inputString.setCharAt(0,' ');
  int mm=inputString.toInt();
  error_step = mm;
  Serial.print("ErrorStep=");
  Serial.println(error_step);
  inputString="";
}
void ErrorSpeed()
{
  inputString.setCharAt(0,' ');
  int mm=inputString.toInt();
  error_speed = mm;
  Serial.print("ErrorSpeed=");
  Serial.println(error_speed);
  inputString="";
}
void MicroStep()
{
  inputString.setCharAt(0,' ');
  int mm=inputString.toInt();
  Microstep = mm;
  Serial.print("Microstep=");
  Serial.println(Microstep);
  inputString="";
}
void Save(boolean mode)
{
  if (mode == true){
    Serial.println("Saved...");
  }
  int arr[] = {X,MoveSpeed,error_step,SwapSpeed_fast,SwapSpeed_low,Microstep};
  for(int i=0;i <sizeof(arr)/sizeof(arr[0]);i++)
  {
    byte hiByte = highByte(arr[i]);
    byte loByte = lowByte(arr[i]);
    EEPROM.write(i*2,hiByte);
    EEPROM.write(i*2+1,loByte);
  }
  inputString="";
}
void Ratio_l(){
  inputString.setCharAt(0,' ');
  int a = inputString.toInt();
  SwapSpeed_low = a;
  Serial.print("Low=");
  Serial.println(SwapSpeed_low);
  inputString="";
}
void Ratio_f(){
  inputString.setCharAt(0,' ');
  int a = inputString.toInt();
  SwapSpeed_fast = a;
  Serial.print("Fast=");
  Serial.println(SwapSpeed_fast);
  inputString="";
}

void IR()
{
  VIR1 = analogRead(IR1);
  VIR2 = analogRead(IR2);
  VIR3 = analogRead(IR3);
  VIR4 = analogRead(IR4);
  roller_value = analogRead(roller);
  VBt1 = digitalRead(Bt1);
  VBt2 = digitalRead(Bt2);
  VBt3 = digitalRead(Bt3);
  VBt4 = digitalRead(Bt4);
  Vm   = digitalRead(Manual);
  Serial.print("Input=");
  Serial.print(VIR1);
  Serial.print(',');
  Serial.print(VIR2);
  Serial.print(',');
  Serial.print(VIR3);
  Serial.print(',');
  Serial.print(VIR4);
  Serial.print(',');
  Serial.print(VBt1);
  Serial.print(',');
  Serial.print(VBt2);
  Serial.print(',');
  Serial.print(VBt3);
  Serial.print(',');
  Serial.print(VBt4);
  Serial.print(',');
  Serial.print(Vm);
  Serial.print(',');
  Serial.println(roller_value);
  
  inputString="";
}
void Target(int t)
{
int mm;
count = 0;
int VIR;
if(t == 0){
  inputString.setCharAt(0,' ');
  mm=inputString.toInt();
  if(mm > 4 || mm < 1){
    return;
  }else{
    Serial.print("target=");
    Serial.println(mm);
    inputString="";
}
}else{
  mm = t;
}
digitalWrite (X_DIR_5v,HIGH);
if(mm == 1){VIR = analogRead(IR1);}
if(mm == 2){VIR = analogRead(IR2);}
if(mm == 3){VIR = analogRead(IR3);}
if(mm == 4){VIR = analogRead(IR4);}
while(true)
{
     if(X % 10 == 0){
      if(mm == 1){VIR = analogRead(IR1);}
      if(mm == 2){VIR = analogRead(IR2);}
      if(mm == 3){VIR = analogRead(IR3);}
      if(mm == 4){VIR = analogRead(IR4);}
      if(VIR < 30){count = count + 1;}else{count = 0;}
      if(count > 3){X = Microstep / 4 * (mm - 1);break;}
      }
     
     if(stop_value == 1){break;}
     if(X == Microstep*2){X = Microstep;}
     while (Serial.available()) 
        {
          char inChar = (char)Serial.read();   
          if (inChar > 0)     {inputString += inChar;}  // add it to the inputString:
          if (inChar == '\n') { stringComplete = true;} // if the incoming character is a newline, set a flag so the main loop can do something about it: 
        }
      if (stringComplete) 
       {  
        if (inputString=="nstate\n"){State(); }
        if (inputString=="Stop\n")  {stop_value = true; swap_stop =true;Serial.println("stoping.."); break;  }
        if (inputString !="") {Serial.print("BAD COMMAND="+inputString);}// Serial.print("\n"); }// "\t" tab      
        inputString = ""; stringComplete = false; // clear the string:
        if(RS == false){digitalWrite (Receive,HIGH);RS=true;}else{digitalWrite (Receive,LOW);RS=false;}
       }
     digitalWrite (X_STP_5v, HIGH);
     digitalWrite (LMove, HIGH);
     delayMicroseconds(MoveSpeed);
     digitalWrite (X_STP_5v, LOW);
     digitalWrite (LMove, LOW);
     delayMicroseconds(MoveSpeed);
     X = X + 1;
}
inputString="";
}
void potential(){
  stop_value = 2;
  digitalWrite (LManual, HIGH);
  while(true){
    roller_value = analogRead(roller);
    VBt1 = digitalRead(Bt1);
    VBt2 = digitalRead(Bt2);
    VBt3 = digitalRead(Bt3);
    VBt4 = digitalRead(Bt4);

    if(VBt1 == 1 && Mm != 1){Mm = 1;Target(1);}
    if(VBt2 == 1 && Mm != 2){Mm = 2;Target(2);}
    if(VBt3 == 1 && Mm != 3){Mm = 3;Target(3);}
    if(VBt4 == 1 && Mm != 4){Mm = 4;Target(4);}
    
    //원하는 위치에 위치하지 않을경우 해당위치로 이동.
    if(Mm == 1){VIR = analogRead(IR1);}
    if(Mm == 2){VIR = analogRead(IR2);}
    if(Mm == 3){VIR = analogRead(IR3);}
    if(Mm == 4){VIR = analogRead(IR4);}
    if(VIR > 30){count = count + 1;}else{count = 0;}
    if(count > 5){count = 0; Target(Mm);}
    
    if(digitalRead(Manual) == HIGH){break;}
    if(X == Microstep*2){X = Microstep;}
    while (Serial.available()) 
    {
      char inChar = (char)Serial.read();   
      if (inChar > 0)     {inputString += inChar;}  // add it to the inputString:
      if (inChar == '\n') { stringComplete = true;} // if the incoming character is a newline, set a flag so the main loop can do something about it: 
    }
    if (stringComplete) 
    {  
    if (inputString=="nstate\n"){State();  }
    if (inputString=="nir\n")       {IR();  }
    if (inputString !="") {Serial.print("BAD COMMAND="+inputString);}    
    inputString = ""; stringComplete = false; // clear the string:
    if(RS == false){digitalWrite (Receive,HIGH);RS=true;}else{digitalWrite (Receive,LOW);RS=false;}
    }
    if(roller_value > 50){MSwap(roller_value);}
  }
  stop_value = 1;
}
void loop()  // **************************************************************     loop
{
  digitalWrite (LManual, LOW);
  if(digitalRead(Manual) == LOW){potential();}
  while (Serial.available()) 
  {
    char inChar = (char)Serial.read();   
    if (inChar > 0)     {inputString += inChar;}  // add it to the inputString:
    if (inChar == '\n') { stringComplete = true;} // if the incoming character is a newline, set a flag so the main loop can do something about it: 
  }
  
 if (stringComplete) 
 {  
  if (inputString.charAt(0)=='s') {MSpeed(); }
  if (inputString.charAt(0)=='k') {Ratio_l(); }
  if (inputString.charAt(0)=='l') {Ratio_f(); }
  if (inputString.charAt(0)=='e') {ErrorStep(); }
  if (inputString.charAt(0)=='p') {ErrorSpeed(); } 
  if (inputString.charAt(0)=='i') {MicroStep(); } 
  if (inputString.charAt(0)=='x') {SetX(); }
  if (inputString.charAt(0)=='t') {stop_value = false; Target(0);stop_value = true; }
  if (inputString.charAt(0)=='m') {stop_value = false; MoveX(0,MoveSpeed,MoveSpeed);stop_value = true;Save(false); } 
  if (inputString.charAt(0)=='r') {stop_value = false; swap_stop  = false; Swap();stop_value = true;Save(false);   }
  if (inputString=="Save\n")      {Save(true);}
  if (inputString=="nstate\n")    {State();  }
  if (inputString=="nir\n")       {IR();  }
  if (inputString !="") {Serial.print("BAD COMMAND="+inputString);}// Serial.print("\n"); }// "\t" tab      
  inputString = ""; stringComplete = false; // clear the string:
  if(RS == false){digitalWrite (Receive,HIGH);RS=true;}else{digitalWrite (Receive,LOW);RS=false;}
 }
}
