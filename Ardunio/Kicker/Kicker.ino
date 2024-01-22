const int outputPin = 8;
void pulsePin(int outputPin, int pulseTime);

void setup() {
  Serial.begin(19200);
  pinMode(outputPin, OUTPUT);
}

void loop() {
  char data;
  if(Serial.available() > 0) {
    data = Serial.read();
    if(data == 'K') {
      pulsePin(outputPin, 200000);
    }
  }
}

void pulsePin(int outputPin, int pulseTime){
  digitalWrite(outputPin, HIGH);
  delayMicroseconds(pulseTime);
  digitalWrite(outputPin,LOW);
}
