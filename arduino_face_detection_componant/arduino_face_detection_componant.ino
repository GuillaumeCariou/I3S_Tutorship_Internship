#define ENB 5
#define IN1 7
#define IN2 8
#define IN3 9
#define IN4 11
#define ENA 6

String nom = "Arduino";
String msg;
int movement = 0;
int speed_forward = 175;
int speed_sideway = 255;
int left = 0;
int right = 0;

void setup() {
  Serial.begin(9600);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void loop() {
  movement = giveMovement();
  
  if(movement == 8){//forward
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    left = speed_forward;
    right = speed_forward;
    Serial.println("forward");
  }else if(movement == 2){//backward
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    left = speed_forward;
    right = speed_forward;
    Serial.println("backward");
    
  }else if(movement == 4){//left
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH); 
    left = speed_sideway;
    right = 0;
    Serial.println("left");
  }else if(movement == 6){//right
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    left = 0;
    right = speed_sideway;
    Serial.println("right");
  }else if (movement == 5){//stop
    left = 0;
    right = 0;
    Serial.println("Stop");
  }

  analogWrite(ENA, left);
  analogWrite(ENB, right);  
}




// Serial Transmition Method
int giveMovement(){
  readSerialPort();
  int nombre = 0;
  if (msg != 0) {
    nombre = msg.toInt();
    sendData(nombre);
  }
  delay(500);

  return nombre;
}

void readSerialPort() {
  msg = "";
  if (Serial.available()) {
    delay(10);
    while (Serial.available() > 0) {
      msg += (char)Serial.read();
    }
    Serial.flush();
  }
}

void sendData(int nombre) {
  //write data
  Serial.print(nom);
  Serial.print(" received : ");
  Serial.print(nombre);
}
