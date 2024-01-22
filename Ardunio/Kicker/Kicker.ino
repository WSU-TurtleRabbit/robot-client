const int outputPin = 8;
void pulsePin(int outputPin, int pulseTime);

void setup() {
  Serial.begin(19200);
  pinMode(outputPin, OUTPUT);

}

void loop() {
  delay(2000);
  pulsePin(outputPin, 200000);
}

void pulsePin(int outputPin, int pulseTime){
  digitalWrite(outputPin, HIGH);
  delayMicroseconds(pulseTime);
  digitalWrite(outputPin,LOW);
}
