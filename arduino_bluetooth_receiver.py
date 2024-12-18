import matplotlib.pyplot as plt
import numpy as np
import threading 
import serial
import time
import random
import csv
import mido
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier

class ArduinoBluetoothReceiver:
    def __init__(self):
        self._bluetooth_connection = None
        self._last_message = ''

    def establish_bluetooth(self, port='COM7', baudrate=9600):
        self._bluetooth_connection = serial.Serial(port, baudrate)
        self._bluetooth_connection.flushInput()
    
    def listen(self) -> None:
        while True:
            input_data = self._bluetooth_connection.readline()
            self._last_message = input_data.decode()

    def start_listening(self) -> None:
        self.listen_thread = threading.Thread(target=self.listen, args=())
        self.listen_thread.daemon = True
        self.listen_thread.start()
        print("Listening...")

class MidiController:
    def __init__(self):
        self._outport = None

    def connect_to_midi(self, name='Gestomat'):
        self._port_name = [m for m in mido.get_output_names() if 'Gestomat' in m][0]
        try:
            self._outport = mido.open_output(self._port_name)
            print(f"[MidiController] Connected to MIDI port: {self._port_name}")
        except Exception as e:
            print(f"Failed to connect to MIDI port: {e}")

    def send(self, msg_type, **data):
        print(f"sending {msg_type=}, {data=}")
        message = mido.Message(msg_type, **data)
        self._outport.send(message)

class ArduinoManager:
    def __init__(self):
        # controllers
        self._arduino_bluetooth_receiver = ArduinoBluetoothReceiver()
        self._midi_controller = MidiController()

        self._current_channel = 0
        self._current_sound = 0
        
        self._velocity_history = []
        self._history_length = 50
        self._activity_threshold = 2
        self._gesture_prob_threshold = 0.75
        self._gesture_cooldown = 2# seconds
        self._gesture_last_time = None

        self._gestures_order = []
        self._gestures_data = None
        self._knn = None

        self._lfo_threshold = 0
        self._lfo_value = 0
        self._lfo_range = [0, 127]

        self._octave_threshold = 0
        self._octave_value = 64
        self._octave_range = (0, 127)

        self._notes = [
            [65, 68, 72, 75, 79]
        ]

    def load_gestures_data(self, path):
        self._gestures_data = pd.read_csv(path)
        X = self._gestures_data[[f'f{i}' for i in range(1, 6)]]
        y = self._gestures_data['gesture']
        self._knn = KNeighborsClassifier(n_neighbors=5)
        self._knn.fit(X, y)

    def load_gestures_names(self, path):
        with open(path, 'r') as f:
            self._gestures = [g.strip() for g in f.readlines()]
        print(f"{self._gestures=}")

    def get_gesture(self):
        if not self._gestures_order:
            self._gestures_order = self._gestures.copy()
            random.shuffle(self._gestures_order)
        random_gesture = self._gestures_order.pop(0)
        pause = input(f"Make a gesture - {random_gesture}")
        if pause == '0':
            return None
        angles = self.get_knn_data()
        print(f"{angles=}")
        return (*angles, random_gesture)

    def train(self, csv_path):
        training_data = []
        while True:
            gesture_data = self.get_gesture()
            if gesture_data is None:
                break
            print(f"{gesture_data=}")
            gesture_dict = {f'f{i+1}': gesture_data[i] for i in range(5)}
            gesture_dict['gesture'] = gesture_data[5]
            training_data.append(gesture_dict)
        
        keys = training_data[0].keys()

        try:
            with open(csv_path, 'r') as f:
                file_exists = True
        except FileNotFoundError:
            file_exists = False

        with open(csv_path, 'a', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            if not file_exists:
                dict_writer.writeheader()
            dict_writer.writerows(training_data)

    def start_midi(self, name='Gestomat'):
        self._midi_controller.connect_to_midi(name)
        self._midi_controller.send('note_on', channel=0, note=int(65), velocity=1) # F4
        self._midi_controller.send('note_on', channel=1, note=int(68), velocity=1) # As
        self._midi_controller.send('note_on', channel=2, note=int(72), velocity=1) # C5
        self._midi_controller.send('note_on', channel=3, note=int(75), velocity=1) # Es
        self._midi_controller.send('note_on', channel=4, note=int(79), velocity=1) # G5
        
        # self._midi_controller.send('note_on', channel=0, note=int(29), velocity=1) # F1
        # self._midi_controller.send('note_on', channel=1, note=int(32), velocity=1) # As
        # self._midi_controller.send('note_on', channel=2, note=int(36), velocity=1) # C2
        # self._midi_controller.send('note_on', channel=3, note=int(39), velocity=1) # Es
        # self._midi_controller.send('note_on', channel=4, note=int(43), velocity=1) # G2
        
        # self._midi_controller.send('note_on', channel=0, note=int(70), velocity=50) # B4 HEs?
        # self._midi_controller.send('note_on', channel=1, note=int(77), velocity=50) # F5
        # self._midi_controller.send('note_on', channel=2, note=int(84), velocity=50) # C6
        # self._midi_controller.send('note_on', channel=3, note=int(63), velocity=50) # Es
        # self._midi_controller.send('note_on', channel=4, note=int(56), velocity=50) # As

    def start_bluetooth(self, port='COM7', baudrate=9600):
        self._arduino_bluetooth_receiver.establish_bluetooth(port, baudrate)
        self._arduino_bluetooth_receiver.start_listening()

    # base X, base Y base Z, base v X, base v Y, base v Z, [for every finger:] angle
    def get_last_message_split(self):
        msg = self._arduino_bluetooth_receiver._last_message
        msg = msg.strip()
        return [float(v) for v in msg.split(';') if v]
    
    def split_more(self):
        data = self.get_last_message_split()
        base = data[:3]
        base_v = data[3:6]
        print(f"Base: {base}\nBase v: {base_v}")
        for i in range(6):
            angle = data[6+i]
            print(f"Finger {i+1}: {angle=}")
        print()

    def split_speed(self):
        data = self.get_last_message_split()
        base = data[:3]
        v = sum(bv ** 2 for bv in base) ** 0.5 - 9.81
        print(f"{v=}")

    # data for knn
    def get_knn_data(self):
        data = self.get_last_message_split()
        knn_data = data[6:]
        return knn_data
    
    def update_history(self):
        data = self.get_last_message_split()
        velocities = [] #data[3:6]
        for i in range(6):
            # velocities.append(abs(data[7 + i * 2] - 9.81))
            velocities.append(data[6:])
            # TU JAKOS ZMIENIC
        if len(self._velocity_history) >= self._history_length:
            self._velocity_history.pop(0)
        self._velocity_history.append(velocities)

    def detect_low_activity(self):
        # print(f"{self._velocity_history=}")
        # print(f"{np.array(self._velocity_history).flatten()=}")
        all_velocities = np.array(self._velocity_history).flatten()
        activity = all_velocities.mean()
        # activity = np.var(all_velocities)
        print(f"{activity=}")
        return activity <= self._activity_threshold
    
    # detect with knn and do stuff
    def run_gesture(self):
        if self._knn.predict_proba([self.get_knn_data()]).max() >= self._gesture_prob_threshold:
            gesture = self._knn.predict([self.get_knn_data()])

            # zmiana dzwięków
            if gesture == 'gesture1':
                for i in range(5):
                    self._midi_controller.send('note_off', channel=i + self._current_channel, note=self._notes[self._current_sound][i], velocity=0)
                self._current_channel = 0
                self._current_sound = 0
                for i in range(5):
                    self._midi_controller.send('note_on', channel=i + self._current_channel, note=self._notes[self._current_sound][i], velocity=1)
            elif gesture == 'gesture2':
                pass
            elif gesture == 'gesture3':
                pass
            elif gesture == 'gesture4':
                pass
            elif gesture == 'gesture5':
                pass
            elif gesture == 'gesture6':
                pass
            elif gesture == 'gesture7':
                pass
            elif gesture == 'gesture8':
                pass
            elif gesture == 'gesture9':
                pass
            elif gesture == 'gesture10':
                pass
    
    def play_sounds(self):
        data = self.get_last_message_split()
        base_vs = data[3:6]
        angles = data[6:]
        # base = 60
        # octaves = [-7, 0, 7, 14]#[-14, -7, 0, 7, 14]
        print(f"{angles=}, {len(angles)=}")
        print(f"{base_vs=}")

        # efekty
        if abs(base_vs[0]) >= self._lfo_threshold:
            self._lfo_value += base_vs[0]
            self._lfo_value = min(max(self._lfo_value, self._lfo_range[0]), self._lfo_range[1])
            self._midi_controller.send('control_change', channel=9, control=50, value=int(self._lfo_value))

        if abs(base_vs[2]) >= self._octave_threshold:
            self._octave_value += base_vs[2]
            self._octave_value = min(max(self._octave_value, self._octave_range[0]), self._octave_range[1])
            self._midi_controller.send('control_change', channel=9, control=51, value=int(self._octave_value))

        print(f"{int(self._lfo_value)=}, {int(self._octave_value)=}")

        # if base_vs[2] >= self._effect_threshold:
        #     self._midi_controller.send('control_change', channel=9, control=50, value=base_vs[2] * 10)
        # elif base_vs[2] < self._effect_threshold:
        #     self._midi_controller.send('control_change', channel=9, control=50, value=base_vs[2] * 10)
        # else:
        #     self._midi_controller.send('control_change', channel=9, control=50, value=0)
    
        # dzwięki palców
        if len(angles) >= 5:
            for i in range(5):
                if angles[i] > 30:
                    self._midi_controller.send('control_change', channel=i, value=int(min(angles[i], 127)))
                    # self._midi_controller.send('pitchwheel', channel=i, pitch=int(min(angles[i+2]*10, 8000)))
                else:
                    self._midi_controller.send('control_change', channel=i, value=0)

    def turn_midi_off(self):
        for ch in range(5):
            for i in range(128):
                print(f"note off, channel={ch}")
                self._midi_controller.send('note_off', channel=ch, note=i, velocity=0)

    def init_plot(self, rows: int, cols: int, x_lims: list[int] = [0, 100], y_lims: list[int] = [-360, 360]):
        self.fig, self.axes = plt.subplots(rows, cols, figsize=(10, 8))
        
        self.lines = []
        for ax in self.axes.flat:
            line, = ax.plot([], [], 'r-')
            ax.set_xlim(x_lims[0], x_lims[1])
            ax.set_ylim(y_lims[0], y_lims[1])
            self.lines.append(line)
        
        self.data = [[] for _ in range(rows * cols)]
        
        plt.ion()
        plt.tight_layout()
        plt.show()

    def plot_all_axes(self):
        values = self.get_last_message_split()

        for i, (line, value) in enumerate(zip(self.lines, values)):
            self.data[i].append(value)
            
            data_vals = self.data[i][-100:]
            
            line.set_data(range(len(data_vals)), data_vals)
            self.axes.flat[i].set_xlim(max(0, len(data_vals) - 100), len(data_vals))

        plt.pause(0.02)

    def plot_real_time(self):
        x_data = [[] for _ in range(12)]
        y_data = [[] for _ in range(12)]
        
        for ax in self.axes.flat:
            ax.set_xlim(0, 100)
            ax.set_ylim(-15, 15)

        while True:
            data = self.get_last_message_split()

            for i, ax in enumerate(self.axes.flat):
                x_data[i].append(len(x_data[i])) 
                y_data[i].append(data[i])

                if len(x_data[i]) > 100:
                    x_data[i] = x_data[i][-100:]
                    y_data[i] = y_data[i][-100:]

                ax.cla()
                ax.plot(x_data[i], y_data[i], color='blue')
                ax.set_xlim(x_data[i][0], x_data[i][-1])
                ax.set_ylim(-15, 15)

            plt.pause(0.1)
    
if __name__ == "__main__":
    try:
        arduino_manager = ArduinoManager()
        arduino_manager.start_bluetooth()
        # arduino_manager.load_gestures_data(r'C:\Users\gtraw\OneDrive\Pulpit\Projekty_Github_CV\LearningThings\Arduino\gesture_data_final.csv')
        # time.sleep(2)
        arduino_manager.start_midi("Gestomat")
        arduino_manager.init_plot(11, 1)

        # LEARNING
        time.sleep(2)
        # arduino_manager.load_gestures_names('gestures.txt')
        # arduino_manager.train('gesture_data_final.csv')
        while True:
        #     # arduino_manager.update_history()
        #     # print(f"low activity: {arduino_manager.detect_low_activity()}")
            # arduino_manager.run_gesture()
            # arduino_manager.split_speed()
            # arduino_manager.plot_all_axes()
            print(arduino_manager.get_last_message_split()[:6])
            # arduino_manager.play_sounds()
            time.sleep(0.05)
    except KeyboardInterrupt:
        arduino_manager.turn_midi_off()
        print(f"--- KeyboardInterrupt ---")
    except Exception as e:
        # arduino_manager.turn_midi_off()
        print(f"Exception: {e}")