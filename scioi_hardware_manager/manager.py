import logging

from device_manager.device_manager import DeviceManager
from extensions.joystick.joystick_manager import JoystickManager, Joystick

logger = logging.getLogger('manager')
logger.setLevel('INFO')


class HardwareManager:
    device_manager: DeviceManager
    joysticks: JoystickManager
    callbacks: dict

    def __init__(self):
        self.device_manager = DeviceManager()
        self.device_manager.registerCallback('new_device', self._newDevice_callback)

        self.joysticks = JoystickManager()
        self.joysticks.registerCallback('new_joystick', self._newJoystickConnected)
        self.joysticks.registerCallback('joystick_disconnected', self._joystickDisconnected)

        self.callbacks = {
            'stream': [],
            'robot_connected': [],
            'robot_disconnected': [],
        }

    def registerCallback(self, callback_id, callback):
        if callback_id in self.callbacks.keys():
            self.callbacks[callback_id].append(callback)
        else:
            raise Exception(f"TCP Device: No callback with id {callback_id} is known.")

    def init(self):
        self.device_manager.init()

    def start(self):
        logger.info("Starting Hardware Manager")
        self.device_manager.start()

    def _newDevice_callback(self, device, *args, **kwargs):
        device.registerCallback('stream', self._rxStream_Callback)
        if device.information.device_class == 'robot':
            for callback in self.callbacks['robot_connected']:
                callback(device)

    def _rxStream_Callback(self, stream, device, *args, **kwargs):
        for callback in self.callbacks['stream']:
            callback(stream, device)

    def _newJoystickConnected(self, joystick: Joystick):
        ...

    def _joystickDisconnected(self, joystick):
        ...