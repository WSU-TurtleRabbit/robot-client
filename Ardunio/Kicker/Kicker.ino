const int outputPin = 8;
uint32_t previousTime = 0;
uint32_t pulseTime = 1000; // pulseTime is in milliseconds
bool pinStatus = LOW;

bool checkPulsePin(bool, int, uint32_t, uint32_t, uint32_t) ; // function statement for compiling

void setup() {
  Serial.begin(19200); // set baudrate to 19200
  pinMode(outputPin, OUTPUT); // set outputPin mode to output
  while(Serial.available() != 1); // wait until serial communications is working 
}

void loop() {
  char data;
  uint32_t currentTime = millis();
  pinStatus = checkPulsePin(pinStatus, outputPin, previousTime, currentTime, pulseTime);
  data = Serial.read();
  if(data == 'K') {
    // check if `pinStatus` is still high from previous pulse
    if(pinStatus == LOW) {
      pinStatus = HIGH;
      previousTime = currentTime;
    }
  }
  digitalWrite(outputPin, pinStatus);
}

bool checkPulsePin(bool pinStatus, int outputPin, uint32_t previousTime, uint32_t currentTime, uint32_t pulseTime) {
  // if `previousTime` has been updated, check it has been longer than `pulseTime`
  if(currentTime - previousTime >= pulseTime) {
    pinStatus = LOW;
  }
  return pinStatus;
}
