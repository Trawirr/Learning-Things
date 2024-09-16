import sys, threading, queue, serial
import serial.tools.list_ports

class ArduinoReceiver:
    def __init__(self) -> None:
        self.devices = []
        self.selected_device = None
        self.connection = None

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

        self.select_device = self.devices[choice].device
        print(f"Selected device: {self.select_device}")

    def connect(self, baudrate=115200, timeout=0.1) -> None:
        self.connection = serial.Serial(self.selected_device, baudrate=baudrate, timeout=timeout)
        if self.connection:
            print(f"Connected to {self.select_device}")

ard_receiver = ArduinoReceiver()
ard_receiver.select_device()
ard_receiver.connect()