import tflite_runtime.interpreter as tflite
import numpy as np
import csv
import sounddevice as sd

# This class is a wrapper around the sound classification model.
class SoundClassifier:
    def __init__(self, model_path, class_map_csv_path, duration=1, sample_rate=16000):
        self.duration = duration
        self.sample_rate = sample_rate
        self.interpreter = tflite.Interpreter(model_path) # Load the tflite model
        self.class_names = self.class_names_from_csv(class_map_csv_path) # Read class names from the CSV file
        self.input_details = self.interpreter.get_input_details()
        self.waveform_input_index = self.input_details[0]['index']
        self.output_details = self.interpreter.get_output_details()
        self.scores_output_index = self.output_details[0]['index']
        self.embeddings_output_index = self.output_details[1]['index']
        self.spectrogram_output_index = self.output_details[2]['index']

    @staticmethod
    def class_names_from_csv(class_map_csv_text):
        """Returns list of class names corresponding to score vector."""
        class_names = []
        with open(class_map_csv_text, 'r') as file:
            reader = csv.reader(file)
            next(reader) # skip first row
            for row in reader:
                class_names.append(row[0])
        return class_names

    def record_sound(self):
        """records a sound with the duration given in the constructor and returns it as a numpy array."""
        recording = sd.rec(int(self.duration * self.sample_rate), 
                           samplerate=self.sample_rate, channels=1, dtype=np.float32)
        sd.wait()  # Wait until recording is finished
        waveform = np.squeeze(recording)
        return waveform

    def classify_sound(self, waveform):
        """Takes a waveform and returns its classification scores, embeddings, and spectrogram."""
        self.interpreter.resize_tensor_input(self.waveform_input_index, [len(waveform)], strict=True)
        self.interpreter.allocate_tensors()
        self.interpreter.set_tensor(self.waveform_input_index, waveform)
        self.interpreter.invoke()
        scores, embeddings, spectrogram = (
            self.interpreter.get_tensor(self.scores_output_index),
            self.interpreter.get_tensor(self.embeddings_output_index),
            self.interpreter.get_tensor(self.spectrogram_output_index))
        return scores, embeddings, spectrogram

    def print_class_score(self, scores, class_indexes):
        """Prints the mean score of passed classes, and the name of the class."""
        for index in class_indexes:
            print(f'The score of {self.class_names[index]} is: {scores.mean(axis=0)[index]} \n')


# usage example:
# classifier = SoundClassifier('./lite-model_yamnet_tflite_1.tflite', './class_names_cleaned.csv')
# waveform = classifier.record_sound()
# scores, embeddings, spectrogram = classifier.classify_sound(waveform)
# print(classifier.class_names[scores.mean(axis=0).argmax()]) # Should print 'Silence'.
# classifier.print_class_score(scores, [316, 318, 390, 391, 382])
