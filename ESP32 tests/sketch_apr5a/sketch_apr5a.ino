// Pin connected to the microphone
const int microphonePin = 32; // Use a suitable ADC pin: GPIO 34

#define SAMPLE_INTERVAL_MS 1 //when 0.25 -> // 1 / 4000 Hz * 1000 ms

// Setup function
void setup() {
  // Start serial communication at 9600 baud
  Serial.begin(38400);

  // Set the microphone pin as input
  pinMode(microphonePin, INPUT);
}

// Loop function
void loop() {
  // Read the analog input from the microphone
  int micData = analogRead(microphonePin);

  // Send the microphone data to the Python script via serial communication
  Serial.println(micData);

  // Small delay to avoid overwhelming the serial buffer
  delay(SAMPLE_INTERVAL_MS); // Adjust the sampling interval
}
