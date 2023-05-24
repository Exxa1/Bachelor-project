# THIS IS 1.5 SECOND INPUT!

#include <Arduino.h>
#include <Wire.h>

// Constants
const int MIC_PIN = A0; // Analog input pin for MAX4466 microphone
const int SAMPLING_RATE = 16000; // Sampling rate for the audio (16 kHz)
const int BUFFER_SIZE = 24000; // Buffer size to store 1.5 seconds of audio (1.5 * 16000)
const int SAMPLES_PER_UPDATE = 8000; // Number of samples to record per update (0.5 * 16000)

// Variables
int audio_tape[BUFFER_SIZE];
int audio_temp[SAMPLES_PER_UPDATE];
unsigned long last_update_time = 0;

void setup() {
  // Initialize the MAX4466 microphone
  pinMode(MIC_PIN, INPUT);
  analogReadResolution(10); // 10-bit resolution for the analog input

  // Start the serial communication
  Serial.begin(115200);
}

void loop() {
  // Check if it's time to update the audio_tape
  unsigned long current_time = millis();
  if (current_time - last_update_time >= 500) { // 0.5 seconds passed
    last_update_time = current_time;

    // Record audio for 0.5 seconds
    for (int i = 0; i < SAMPLES_PER_UPDATE; i++) {
      audio_temp[i] = analogRead(MIC_PIN);
      delayMicroseconds(1000000 / SAMPLING_RATE); // Wait for the next sample
    }

    // Update the audio_tape
    memcpy(audio_tape, audio_tape + SAMPLES_PER_UPDATE, (BUFFER_SIZE - SAMPLES_PER_UPDATE) * sizeof(int));
    memcpy(audio_tape + (BUFFER_SIZE - SAMPLES_PER_UPDATE), audio_temp, SAMPLES_PER_UPDATE * sizeof(int));

    // Send the audio_tape data to the Python script via serial communication
    for (int i = 0; i < BUFFER_SIZE; i++) {
      Serial.write((byte*)&audio_tape[i], sizeof(int));
    }
  }
}
