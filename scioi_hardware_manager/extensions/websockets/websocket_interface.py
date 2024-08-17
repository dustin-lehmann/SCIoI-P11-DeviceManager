from extensions.websockets.websocket_server import WebsocketClass
from applications.robot_manager import RobotManager
from extensions.joystick.joystick_manager import Joystick
import json
from device_manager.devices.robots.twipr.twipr import TWIPR
import time

class WebsocketInterface():

    def __init__(self, stream_ws_host: str, stream_ws_port: int, message_ws_host: str, message_ws_port: int, robot_manager: RobotManager, logging: bool = True):
        self.stream_ws = WebsocketClass(stream_ws_host, stream_ws_port)
        self.message_ws = WebsocketClass(message_ws_host, message_ws_port)
        self.stream_ws.run()
        self.message_ws.run()
        self.message_ws.set_message_callback(self._message_callback)
        self.robot_manager = robot_manager
        self.controlModeDict = {"off": 0, "direct": 1, "balancing": 2, "speed": 3}
        self.COMMAND_MESSAGE = 'command'
        self.JOYSTICKS_CHANGED_MESSAGE = 'joysticksChanged'
        self.SET_CONTROL_MODE_MESSAGE = 'set'
        self.SET_CONTROLLER_PARAMETERS_MESSAGE = 'setControllerParameters'
        self.EMERGENCY_MESSAGE = 'emergency'
        self.UNASSIGNED_BOT_ID = ''
        self.joysticks = []
        self.robot_manager.registerCallback('new_robot', self._robot_connect_callback)
        self.robot_manager.registerCallback('robot_disconnected', self._robot_disconnect_callback)
        self.robot_manager.joysticks.registerCallback('new_joystick', self._joystick_connect_callback)
        self.robot_manager.joysticks.registerCallback('joystick_disconnected', self._joystick_disconnect_callback)
        self.robot_manager.registerCallback('stream', self._robot_stream_callback)
        self.logging = logging
        self.message_ws.set_connection_callback(self._new_client_connected)
        self._send_initial_values()

    
    def send_stream(self, stream):
        self.stream_ws.send(stream)
    

    def send_message(self, message):
        self.message_ws.send(message)
    

    def _message_callback(self, message):
        data = json.loads(message)
        message_type = data.get('type')
        if message_type == self.COMMAND_MESSAGE:
            self._command_message_handling(data)
        elif message_type == self.JOYSTICKS_CHANGED_MESSAGE:
            self._joysticksChanged_message_handling(data)
        elif message_type == self.SET_CONTROL_MODE_MESSAGE:
            self._set_message_handling(data)
        elif message_type == self.SET_CONTROLLER_PARAMETERS_MESSAGE:
            self._set_controller_parameters_message_handling(data)
        else:
            print(f"ERROR: Unknown message type: {message_type}")
        

    def _command_message_handling(self, data):
        if data.get('data').get('command') == self.EMERGENCY_MESSAGE:
            timestamp = data.get('timestamp')
            self.robot_manager.emergencyStop()
            if self.logging:
                print(f"Emergency command received at {timestamp}")
        else:
            print(f"ERROR: Unknown command message: {data.get('data').get('command')}")
    

    def _joysticksChanged_message_handling(self, data):
        joysticks = data.get('data')
        for joystrick in joysticks:
            controller_id = joystrick.get('id')
            bot_id = joystrick.get('assignedBot')
            if bot_id == self.UNASSIGNED_BOT_ID:
                if controller_id in self.robot_manager.joystick_assignments.keys():
                    self.robot_manager.unassignJoystick(controller_id)
                    if self.logging:
                        print(f"Unassigning controller {controller_id}")
            else:
                if controller_id in self.robot_manager.joystick_assignments.keys():
                    connected_bot_id = self.robot_manager.joystick_assignments[controller_id]['robot'].device.information.device_id
                    if connected_bot_id == bot_id:
                        pass
                    else:
                        self.robot_manager.assignJoystick(bot_id, controller_id)
                else:
                    self.robot_manager.assignJoystick(bot_id, controller_id)
            timestamp = data.get('timestamp')
            if self.logging:
                print(f"Assigning controller {controller_id} to bot {bot_id} at {timestamp}")
    

    def _set_message_handling(self, data):
        bot_id = data.get('botId')
        key = data.get('data').get('key')
        value = data.get('data').get('value')
        timestamp = data.get('timestamp')
        modeId = self.controlModeDict.get(value)
        self.robot_manager.setRobotControlMode(bot_id, modeId)
        if self.logging:
            print(f"Setting {key} to {value} ({modeId}) for bot {bot_id} at {timestamp}")


    def _set_controller_parameters_message_handling(self, data):
        print("Not implemented yet")
    

    def _robot_connect_callback(self, robot, *args, **kwargs):
        message = {"event": "robot_connected", "device_id": robot.device.information.device_id}
        self.message_ws.send(message)
        if self.logging:
            print(f"New Robot connected ({robot.device.information.device_name})")
    

    def _robot_disconnect_callback(self, robot, *args, **kwargs):
        message = {"event": "robot_disconnected", "device_id": robot.device.information.device_id}
        self.message_ws.send(message)
        if self.logging:
            print(f"Robot disconnected ({robot.device.information.device_name})")
    

    def _joystick_connect_callback(self, joystick, *args, **kwargs):
        id = joystick.uuid
        name = joystick.name
        for j in self.joysticks:
            if j.get('id') == id:
                return
        joy = {"id": id, "name": name, "assignedBot": ""}
        self.joysticks.append(joy)
        message = { "timestamp" : time.time(), "type" : "joysticksChanged", "data": {"joysticks" : joysticks}  }
        self.message_ws.send(message)
        if self.logging:
            print(f"New Joystick connected (ID: {id}, UUID: {joystick.uuid})")

    
    def _joystick_disconnect_callback(self, joystick, *args, **kwargs):
        id = joystick.uuid
        for joy in self.joysticks:
            if joy.get('id') == id:
                self.joysticks.remove(joy)
                message = { "timestamp" : time.time(), "type" : "joysticksChanged", "data": {"joysticks" : joysticks}  }
                self.message_ws.send(message)
                if self.logging:
                    print(f"Joystick disconnected (ID: {id}, UUID: {joystick.uuid})")
                return


    def _robot_stream_callback(self, robot, stream, *args, **kwargs):
        self.send_stream(stream)
        if self.logging:
            print(f"Stream from {robot.device.information.device_name} sent")
    

    def _send_initial_values(self):
        message = { "timestamp" : time.time(), "type" : "joysticksChanged", "data": {"joysticks" : self.joysticks}  }
        self.message_ws.send(message)
        if self.logging:
            print("Initial values sent")
    

    def _new_client_connected(self):
        self._send_initial_values()
        if self.logging:
            print("New client connected and initial values sent")