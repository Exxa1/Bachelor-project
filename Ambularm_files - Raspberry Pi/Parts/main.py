# Importing the necessary modules.
import Bluetooth_class as bt
import Classifier_class as sr # Sound Recognizer
import time

# Initialization of the SoundClassifier and Bluetooth_manager
classifier = sr.SoundClassifier('./lite-model_yamnet_tflite_1.tflite', './class_names_cleaned.csv') # Loading sound classifier model
phone_mac_address = "A8:34:6A:ED:83:EB"  # Phone's Bluetooth (MAC) Address
uuid = "691e69ed-9e3c-48ff-ab87-851d1ef80f47"  # Same UUID as on Android Application
bluetooth_manager = bt.Bluetooth_manager(phone_mac_address, uuid) # Initializing Bluetooth manager for the given MAC address and UUID

def main():
    message = "Listening..."
    reset = False # Used to reset the app text after 3 seconds to "Listening...".
    bluetooth_manager.send_message_to_phone(message)
    emergency_vehicle_index = 316 # This is the index in the model output for 'Emergency Vehicle' class
    message_time = time.time()

    while(True):
        waveform = classifier.record_sound() # Records a 1-second audio clip
        scores, _embeddings, _spectrogram = classifier.classify_sound(waveform) # Classifies the recorded sound
        main_sound = classifier.class_names[scores.mean(axis=0).argmax()] # Retrieves the most probable sound
        emergency_sound_prediction = scores.mean(axis=0)[emergency_vehicle_index] # Retrieves the 'Emergency Vehicle' class score

        # If the 'Emergency Vehicle' score is above a threshold, sends a message to the phone, and prepares for a message reset.
        if emergency_sound_prediction > 0.0001:
            emergency_sound_prediction_rounded = round(emergency_sound_prediction, 6)
            message = f"Emergency vehicle detected with score {emergency_sound_prediction_rounded}!"
            print("The main sound is: ", main_sound)
            bluetooth_manager.send_message_to_phone(message)
            message_time = time.time()
            reset = True
            continue

        # If no 'Emergency Vehicle' sound has been detected for more than 3 seconds, resets the message to "Listening...".
        if ((time.time() - message_time > 3) and reset):
            message = "Listening..."
            bluetooth_manager.send_message_to_phone(message)
            reset = False
            continue

        # Prints the 'Emergency Vehicle' score. (Other possible scores for siren detection:316, 318, 390, 391, 382)
        classifier.print_class_score(scores, [316])

if __name__ == '__main__':
    try: 
        main()
    except KeyboardInterrupt:
       bluetooth_manager.close_connection() # Ensures the Bluetooth connection is closed before exiting.
       print("Program terminated manually!")
       raise SystemExit