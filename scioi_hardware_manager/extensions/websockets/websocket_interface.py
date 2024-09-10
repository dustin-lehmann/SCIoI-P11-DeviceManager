from extensions.websockets.websocket_server import WebsocketClass
from applications.robot_manager import RobotManager
from extensions.joystick.joystick_manager import Joystick
import json
from device_manager.devices.robots.twipr.twipr import TWIPR
import time

class WebsocketInterface():
    """
    The WebsocketInterface class manages the communication between the robot manager and
    the clients connected through WebSocket. It handles incoming messages, manages joystick 
    connections, and relays streams and messages to the appropriate components.
    """

    def __init__(self, stream_ws_host: str, stream_ws_port: int, message_ws_host: str, message_ws_port: int, robot_manager, logging: bool = True, recording: bool = False, stream_recording_path: str = None, message_recording_path: str = None, dummy: bool = False):
        """
        Initializes the WebsocketInterface with the given WebSocket hosts and ports, and sets up
        the robot manager, joystick manager, and message handling.

        :param stream_ws_host: Host for the stream WebSocket.
        :param stream_ws_port: Port for the stream WebSocket.
        :param message_ws_host: Host for the message WebSocket.
        :param message_ws_port: Port for the message WebSocket.
        :param robot_manager: RobotManager that manages connected robots.
        :param logging: A boolean flag to enable or disable logging (errors are always logged).
        :param recording: A boolean flag to enable or disable recording of WebSocket messages.
        :param stream_recording_path: The path to save the recorded stream messages.
        :param message_recording_path: The path to save the recorded message messages.
        """
        self.stream_ws = WebsocketClass(stream_ws_host, stream_ws_port, False, recording, recording_path=stream_recording_path)
        self.message_ws = WebsocketClass(message_ws_host, message_ws_port, False, recording, recording_path=message_recording_path)
        self.stream_ws.run()
        self.message_ws.run()
        self.message_ws.set_message_callback(self._message_callback)
        self.robot_manager = robot_manager
        self.controlModeDict = {
            "off": 0, 
            "direct": 1, 
            "balancing": 2, 
            "speed": 3
            }
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
        self.recording = recording
        self.message_ws.set_connection_callback(self._new_client_connected)
        self._send_initial_values()

    
    def send_stream(self, stream):
        """
        Sends the stream data through the stream WebSocket.

        :param stream: The data stream to be sent.
        """
        self.stream_ws.send(stream)
    

    def send_message(self, message):
        """
        Sends a message through the message WebSocket.

        :param message: The message to be sent.
        """
        self.message_ws.send(message)
    

    def _message_callback(self, message):
        """
        Callback function that processes incoming messages and delegates them to the appropriate
        handler based on the message type.

        :param message: The received message in JSON format.
        """
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
        """
        Handles 'command' type messages. Processes the command or triggers emergency stop if necessary.

        :param data: The data part of the message containing the command details.
        """
        if data.get('data').get('command') == self.EMERGENCY_MESSAGE:
            timestamp = data.get('timestamp')
            self.robot_manager.emergencyStop()
            if self.logging:
                print(f"Emergency command received at {timestamp}")
        else:
            print(f"ERROR: Unknown command message: {data.get('data').get('command')}")
    

    def _joysticksChanged_message_handling(self, data):
        """
        Handles 'joysticksChanged' type messages. Updates the joystick assignments based on the data provided.

        :param data: The data part of the message containing joystick details.
        """
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
        """
        Handles 'set' type messages. Sets the control mode of the specified robot.

        :param data: The data part of the message containing control mode details.
        """
        bot_id = data.get('botId')
        key = data.get('data').get('key')
        value = data.get('data').get('value')
        timestamp = data.get('timestamp')
        modeId = self.controlModeDict.get(value)
        self.robot_manager.setRobotControlMode(bot_id, modeId)
        if self.logging:
            print(f"Setting {key} to {value} ({modeId}) for bot {bot_id} at {timestamp}")


    def _set_controller_parameters_message_handling(self, data):
        """
        Handles 'setControllerParameters' type messages. (Currently not implemented)

        :param data: The data part of the message containing controller parameters.
        """
        print("Not implemented yet")
    

    def _robot_connect_callback(self, robot, *args, **kwargs):
        """
        Callback function that is triggered when a new robot is connected.
        Sends a notification message about the new robot connection.

        :param robot: The connected robot instance.
        """
        message = {
            "event": "robot_connected", 
            "device_id": robot.device.information.device_id
            }
        self.message_ws.send(message)
        if self.logging:
            print(f"New Robot connected ({robot.device.information.device_name})")
    

    def _robot_disconnect_callback(self, robot, *args, **kwargs):
        """
        Callback function that is triggered when a robot is disconnected.
        Sends a notification message about the robot disconnection.

        :param robot: The disconnected robot instance.
        """
        message = {
            "event": "robot_disconnected", 
            "device_id": robot.device.information.device_id
            }
        self.message_ws.send(message)
        if self.logging:
            print(f"Robot disconnected ({robot.device.information.device_name})")
    

    def _joystick_connect_callback(self, joystick, *args, **kwargs):
        """
        Callback function that is triggered when a new joystick is connected.
        Adds the joystick to the list and sends a notification message.

        :param joystick: The connected joystick instance.
        """
        id = joystick.uuid
        name = joystick.name
        for j in self.joysticks:
            if j.get('id') == id:
                return
        joy = {"id": id, "name": name, "assignedBot": ""}
        self.joysticks.append(joy)
        message = { 
            "timestamp" : time.time(), 
            "type" : "joysticksChanged", 
            "data": {"joysticks" : joysticks}
            }
        self.message_ws.send(message)
        if self.logging:
            print(f"New Joystick connected (ID: {id}, UUID: {joystick.uuid})")

    
    def _joystick_disconnect_callback(self, joystick, *args, **kwargs):
        """
        Callback function that is triggered when a joystick is disconnected.
        Removes the joystick from the list and sends a notification message.

        :param joystick: The disconnected joystick instance.
        """
        id = joystick.uuid
        for joy in self.joysticks:
            if joy.get('id') == id:
                self.joysticks.remove(joy)
                message = { 
                    "timestamp" : time.time(), 
                    "type" : "joysticksChanged", 
                    "data": {"joysticks" : joysticks}
                    }
                self.message_ws.send(message)
                if self.logging:
                    print(f"Joystick disconnected (ID: {id}, UUID: {joystick.uuid})")
                return


    def _robot_stream_callback(self, robot, stream, *args, **kwargs):
        """
        Callback function that is triggered when a robot sends a stream.
        Forwards the stream data to the appropriate WebSocket.

        :param robot: The robot instance that is sending the stream.
        :param stream: The stream data to be forwarded.
        """
        self.send_stream(stream)
        if self.logging:
            print(f"Stream from {robot.device.information.device_name} sent")
        

    def _send_initial_values(self):
        """
        Sends the initial values to the connected client. This typically includes
        the current state of all joysticks. This function is called when a new 
        client connects or when the WebsocketInterface is initialized.
        """
        message = { 
            "timestamp" : time.time(), 
            "type" : "joysticksChanged", 
            "data": {"joysticks" : self.joysticks}  
        }
        self.message_ws.send(message)
        if self.logging:
            print("Initial values sent")
        

    def _new_client_connected(self):
        """
        Callback function that is triggered when a new client connects to the message WebSocket.
        Sends the initial joystick values to the newly connected client.

        This ensures that the client is synchronized with the current state of the system
        as soon as the connection is established.
        """
        self._send_initial_values()
        if self.logging:
            print("New client connected and initial values sent")