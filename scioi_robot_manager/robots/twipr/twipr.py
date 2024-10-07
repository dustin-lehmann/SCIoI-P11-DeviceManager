import dataclasses
import time

from core.devices.device import Device
from robots.twipr.utils.twipr_data import TWIPR_Data, twiprSampleFromDict
from utils.performance import timer
from utils.logging import Logger

logger = Logger("TWIPR")
logger.setLevel("DEBUG")


class TWIPR:
    device: Device
    callbacks: dict
    data: TWIPR_Data

    def __init__(self, device: Device, *args, **kwargs):
        self.device = device

        self.callbacks = {
            'stream': []
        }

        self.data = TWIPR_Data()
        self.device.registerCallback('stream', self._onStreamCallback)

    # === CLASS METHODS =====================================================================

    # === METHODS ============================================================================

    # === PROPERTIES ============================================================================
    @property
    def id(self):
        return self.device.information.device_id

    # === COMMANDS ===========================================================================

    def balance(self, state):
        self.setControlMode(2)

    def resetEncoder(self):
        self.device.command(command='resetEncoder',
                            data=[])

    def setControlConfiguration(self, config):
        ...

    def loadControlConfiguration(self, name):
        ...

    def saveControlConfiguration(self, name):
        ...

    def beep(self, time):
        ...

    def stop(self):
        self.setControlMode(0)

    def setControlMode(self, mode):
        logger.debug(f"Robot {self.id}: Set Control Mode to {mode}")
        self.device.command(command='setControlMode', data={'mode': mode})

    def setInput(self, input, *args, **kwargs):
        self.device.command('setControlInput', data={'input': input})

    def setTorque(self, torque, *args, **kwargs):
        self.device.command('setControlInput', data={'input': torque})

    def setLEDs(self, color):
        ...

    def setTestParameter(self, value):
        ...

    def setSpeed(self, v, psi_dot):
        ...

    def _onStreamCallback(self, stream, *args, **kwargs):
        self.data = twiprSampleFromDict(stream.data)