import Bluetooth_class as bt
import Classifier_class as sr # Sound Recognizer
import time


classifier = sr.SoundClassifier('./lite-model_yamnet_tflite_1.tflite', './class_names_cleaned.csv')
phone_mac_address = "A8:34:6A:ED:83:EB"  # Phone's Bluetooth (MAC) Address
uuid = "691e69ed-9e3c-48ff-ab87-851d1ef80f47"  # Same UUID as on Android Application
bluetooth_manager = bt.Bluetooth_manager(phone_mac_address, uuid)


def main():

    message = "Listening..."
    reset = False # Used to reset the app text after 3 seconds to "Listening...".
    bluetooth_manager.send_message_to_phone(message)
    emergency_vehicle_index = 316
    message_time = time.time()

    while(True):
        waveform = classifier.record_sound()
        scores, _embeddings, _spectrogram = classifier.classify_sound(waveform)
        main_sound = classifier.class_names[scores.mean(axis=0).argmax()]
        emergency_sound_prediction = scores.mean(axis=0)[emergency_vehicle_index]

        if emergency_sound_prediction > 0.0001:
            emergency_sound_prediction_rounded = round(emergency_sound_prediction, 6)
            message = f"Emergency vehicle detected with score {emergency_sound_prediction_rounded}!"
            print("The main sound is: ", main_sound)

            bluetooth_manager.send_message_to_phone(message)
            message_time = time.time()
            reset = True
            continue
        
        if ((time.time() - message_time > 3) and reset):
            message = "Listening..."
            bluetooth_manager.send_message_to_phone(message)
            reset = False
            continue

        # Important scores for siren detection:316, 318, 390, 391, 382
        classifier.print_class_score(scores, [316])


if __name__ == '__main__':
    try: main()
    except KeyboardInterrupt:
       bluetooth_manager.close_connection()
       print("Program terminated manually!")
       raise SystemExit
    