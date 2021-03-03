#define ENB 5
#define IN1 7
#define IN2 8
#define IN3 9
#define IN4 11
#define ENA 6

struct Movement{
  int left;
  int right;
  int Just_send;
};

String nom = "Arduino_Elegoo";
Movement movement = {0,0,0};
Movement mov = {0,0,0};

int speed_forward = 175;
int speed_sideway = 255;

void setup() {
  Serial.begin(9600);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);
}

void loop() {
  movement = giveMovement();

  /*
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
  }*/

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  
  analogWrite(ENA, mov.left);
  analogWrite(ENB, mov.right);  
}




// Serial Transmition Method
Movement giveMovement(){
  readSerialPort();
  if (mov.Just_send != 0) {
    //mov = msg.toInt();
    sendData(mov);
  }
  delay(500);

  return mov;
}

Movement readSerialPort() {
  mov = {movement.left,movement.right,0};
  String msg;
  String strArr[2];
  if (Serial.available()) {
    delay(10);
    while (Serial.available() > 0) {
      msg += (char)Serial.read();
    }
    
    Serial.flush();

    int stringStart = 0;
    int arrayIndex = 0;
    
    for (int i=0; i < msg.length(); i++){
      if(msg.charAt(i) == ','){
        strArr[arrayIndex] = "";
        strArr[arrayIndex] = msg.substring(stringStart, i);
        stringStart = (i+1);
        arrayIndex++;
      }
    }
    mov.left = strArr[0].toInt();
    mov.right = strArr[1].toInt();
    mov.Just_send = 1;
  }
  
  return mov;
}

void sendData(Movement mov) {
  //write data
  Serial.print(nom);
  Serial.print(" received left: ");
  Serial.print(mov.left);
  Serial.print(" received right: ");
  Serial.print(mov.right);
  Serial.print("\n\n");
}
