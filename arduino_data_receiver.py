import sys, threading, queue, serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from scipy.io import wavfile
import pyaudio
import numpy as np
import librosa

import time

class ArduinoReceiver:
    def __init__(self) -> None:
        self.devices = []
        self.selected_device = None
        self.connection = None
        self.listen_thread = None
        self.queue = queue.Queue()

        self.message = None

    def fetch_available_devices(self) -> None:
        self.devices = serial.tools.list_ports.comports()

    def print_available_devices(self) -> None:
        print("device\tname\tmanufacturer")
        for index, value in enumerate(sorted(self.devices)):
            if (value.hwid != 'n/a'):
                print(index, '\t', value.name, '\t', value.manufacturer)

    def select_device(self) -> None:
        self.fetch_available_devices()
        self.print_available_devices()

        choice = -1
        devices_ids = list(range(len(self.devices)))
        while choice not in devices_ids:
            print("Select device: ", end="")
            choice = int(input())

        self.selected_device = self.devices[choice].device
        print(f"Selected device: {self.selected_device}")

    def connect(self, baudrate=9600, timeout=0.1) -> None:
        self.connection = serial.Serial(self.selected_device, baudrate=baudrate, timeout=timeout)
        if self.connection:
            print(f"Connected to {self.selected_device}")
            print(self.connection)

    def listen(self) -> None:
        message_tmp = b''
        while True:
            data = self.connection.read()
            # self.message ended
            if (data == b'\n'):
                self.queue.put(message_tmp.decode('utf-8').strip().upper())
                self.message = message_tmp
                message_tmp = b''
            elif data:
                message_tmp += data

    def start_listening(self) -> None:
        self.listen_thread = threading.Thread(target=self.listen, args=())
        self.listen_thread.daemon = True
        self.listen_thread.start()
        print("Listening...")

    def read_last(self) -> str:
        if self.message:
            return self.message
        return None

class AccelerometerManager:
    def __init__(self) -> None:
        self._ard_receiver = ArduinoReceiver()

    def start_arduino(self):
        self._ard_receiver.select_device()
        self._ard_receiver.connect()
        self._ard_receiver.start_listening()

    def get_last_message(self):
        return self._ard_receiver.read_last()
    
    def get_last_message_split(self) -> list[int]:
        msg = self._ard_receiver.read_last().decode("utf-8")
        msg = msg.strip()
        print(msg)
        x, y, z = msg.split(';')
        return x, y, z
    
    def init_plot(self):
        self.fig, self.axes = plt.subplots(3, 1, figsize=(8, 6))
        self.line_x, = self.axes[0].plot([], [], 'r-', label='x')
        self.line_y, = self.axes[1].plot([], [], 'g-', label='y')
        self.line_z, = self.axes[2].plot([], [], 'b-', label='z')

        for ax in self.axes:
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 255)
            ax.legend(loc="upper right")

        self.data_x = []
        self.data_y = []
        self.data_z = []

        plt.ion()
        plt.tight_layout()
        plt.show()

    def plot_xyz(self):
        x, y, z = self.get_last_message_split()
        self.data_x.append(int(x))
        self.data_y.append(int(y))
        self.data_z.append(int(z))

        x_vals = self.data_x[-100:]
        y_vals = self.data_y[-100:]
        z_vals = self.data_z[-100:]

        self.line_x.set_data(range(len(x_vals)), x_vals)
        self.line_y.set_data(range(len(y_vals)), y_vals)
        self.line_z.set_data(range(len(z_vals)), z_vals)

        for ax, values in zip(self.axes, (x_vals, y_vals, z_vals)):
            ax.set_xlim(max(0, len(values) - 100), len(values))

        plt.pause(0.02)

    def load_sounds(self):
        self.sound_filenames = [
            fr'C:\Users\gtraw\OneDrive\Pulpit\Projekty_Github_CV\LearningThings\Arduino\sounds\{i}.wav' for i in range(2, 7)
        ]
        self.sounds = {filename: wavfile.read(filename) for filename in self.sound_filenames}
        self.modifiers = {filename: [0, 0] for filename in self.sound_filenames}

    def start_sound_thread(self, filename, modifier):
        thread = threading.Thread(target=self.play_sound_thread, args=(filename, modifier))
        thread.start()

    def play_sound(self, filename):
        print(f"playing {filename}")
        sample_rate, data = wavfile.read(filename)
        
        print(data.shape, data[0])
        data = np.int16(data) 
        print(data.shape, data[0])
        
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=int(sample_rate * modifier), output=True)
        
        stream.write(data.tobytes())
        
        # Cleanup
        stream.stop_stream()
        stream.close()
        p.terminate()

    def play_sounds(self):
        pass

sounds = [
    fr'C:\Users\gtraw\OneDrive\Pulpit\Projekty_Github_CV\LearningThings\Arduino\sounds\{i}.wav' for i in range(2, 7)
]
print(sounds)
am = AccelerometerManager()
am.start_arduino()
time.sleep(0.5)
# am.init_plot()
while True:
    x, y, z = am.get_last_message_split()
    modifier = float(z)/127
    print(f"{modifier=}")
    am.play_sound(np.random.choice(sounds), modifier)
    time.sleep(0.5)
    # am.plot_xyz()