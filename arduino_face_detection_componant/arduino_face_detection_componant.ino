#define ENB 5
#define IN1 7
#define IN2 8
#define IN3 9
#define IN4 11
#define ENA 6

#define Right A2
#define Left A1

#define speed_forward 150


void setup() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);

  pinMode(Right, INPUT);
  pinMode(Left, OUTPUT);
}


void left(){
  digitalWrite(ENA, HIGH);
  digitalWrite(ENB, HIGH);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH); 
  Serial.println("Left");
}

void right(){
  digitalWrite(ENA, HIGH);
  digitalWrite(ENB, HIGH);
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  Serial.println("Right");
}

void forward(){
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);

  analogWrite(ENB, speed_forward);
  analogWrite(ENA, speed_forward);
}

int buttonState = 0;

void loop() {
  /*
  if(digitalRead(Right) == HIGH ){
    right();
    delay(1000);
  }else if(digitalRead(Left) == HIGH ){
    left();
    delay(1000);
  }else{
    forward();
    delay(1000);
  }
  delay(5000);
  */

  buttonState = digitalRead(Right);

  if (buttonState == HIGH) {
    // turn LED on:
    digitalWrite(Left, HIGH);
  } else {
    // turn LED off:
    digitalWrite(Left, LOW);
  }

  
}
