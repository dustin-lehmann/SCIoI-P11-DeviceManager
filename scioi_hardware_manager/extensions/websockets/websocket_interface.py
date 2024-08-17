from extensions.websockets.websocket_server import WebsocketClass
from applications.robot_manager import RobotManager

class WebsocketInterface():

    def __init__(self, stream_ws_host: str, stream_ws_port: int, message_ws_host: str, message_ws_port: int, robot_manager: RobotManager):
        self.stream_ws = WebsocketClass(stream_ws_host, stream_ws_port)
        self.message_ws = WebsocketClass(message_ws_host, message_ws_port)
        self.stream_ws.run()
        self.message_ws.run()
        self.message_ws.set_message_callback(self._message_callback)
        self.robot_manager = robot_manager
    
    def send_stream(self, stream):
        self.stream_ws.send(stream)
    
    def send_message(self, message):
        self.message_ws.send(message)
    
    def _message_callback(self, message):
        data = json.loads(message)
        message_type = data.get('type')

        if message_type == 'command':
            if data.get('data').get('command') == 'emergency':
                timestamp = data.get('timestamp')
                # emergency command at hardwaremanager
                self.robot_manager.emergencyStop()
                print(f"Emergency command received at {timestamp}")
            else:
                print(f"Unknown command message: {data.get('data').get('command')}")

        elif message_type == 'joysticksChanged':
            joysticks = data.get('data')
            for joystrick in joysticks:
                controller_id = joystrick.get('id')
                bot_id = joystrick.get('assignedBot')
                if bot_id == "":
                    # check if the controller is assigned to a bot
                    if controller_id in self.robot_manager.joystick_assignments.keys():
                        self.robot_manager.unassignJoystick(controller_id)
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
                        # check to what bot the controller is assigned
                timestamp = data.get('timestamp')
                # Assign the controller to the bot with hardware manager
                print(f"Assigning controller {controller_id} to bot {bot_id} at {timestamp}")

        elif message_type == 'set':
            bot_id = data.get('botId')
            key = data.get('data').get('key')
            value = data.get('data').get('value')
            timestamp = data.get('timestamp')
            print(f"Setting {key} to {value} for bot {bot_id} at {timestamp}")
            # Set the control mode for the bot using hardware manager
            modeId = controlModeDict.get(value)
            self.robot_manager.setRobotControlMode(bot_id, modeId)

        else:
            print(f"Unknown message type: {message_type}")