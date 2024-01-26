const int outputPin = 8;
void pulsePin(int outputPin, int pulseTime); // function statement for compiling

void setup() {
  Serial.begin(19200); // set baudrate to 19200
  pinMode(outputPin, OUTPUT); // set outputPin mode to output
}

void loop() {
  char data;
  if(Serial.available() > 0) { 
    data = Serial.read();
    if(data == 'K') { // if the data recv'ed is 'K' (note: this is case sensitive)
      pulsePin(outputPin, 200000); 
    }
  }
}

void pulsePin(int outputPin, int pulseTime){
  /*
  * pulsePin(int outputPin, int pulseTime)
  * sends a pulse (active high) into `outputPin` when called.
  * args:
  * outputPin (int): pin to send the pulse to
  * pulseTime (int): length of pulse in microseconds
  */
  digitalWrite(outputPin, HIGH);
  delayMicroseconds(pulseTime);
  digitalWrite(outputPin,LOW);
}
