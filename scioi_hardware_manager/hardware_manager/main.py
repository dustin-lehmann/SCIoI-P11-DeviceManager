import time

from hardware_manager.manager import HardwareManager
from hardware_manager.helper.websocket_server import WebsocketClass
ws_stream = None
ws_messages = None
stop_streaming = False
hardware_manager = None

def stream_callback(stream, device, *args, **kwargs):
    global ws_stream, stop_streaming
    if not stop_streaming:
        ws_stream.send(stream.data)
        print("X")


def new_robot(robot, *args, **kwargs):
    global ws_messages
    print(f"New Robot connected ({robot.information.device_name})")
    message = {"event": "robot_connected", "device_id": robot.information.device_id}
    ws_messages.send(message)


def robot_disconnected(robot, *args, **kwargs):
    global ws_messages
    print(f"Robot disconnected ({robot.information.device_name})")
    message = {"event": "robot_disconnected", "device_id": robot.information.device_id}
    ws_messages.send(message)

def ws_callback(message):
    global stop_streaming
    global hardware_manager
    data = json.loads(message)
    message_type = data.get('type')

    if message_type == 'command' and data.get('command') == 'emergency':
        stop_streaming = True
        timestamp = data.get('timestamp')
        print(f"Emergency command received at {timestamp}")

    elif message_type == 'assignController':
        bot_id = data.get('botId')
        controller_id = data.get('controllerId')
        timestamp = data.get('timestamp')
        # get the controller and the robot
        controller = None
        robot = None
        # assign the controller to the robot
        #hardware_manager.assignController(bot_id, controller_id)
        print(f"Assigning controller {controller_id} to bot {bot_id}")

    elif message_type == 'set':
        bot_id = data.get('botId')
        key = data.get('key')
        value = data.get('value')
        timestamp = data.get('timestamp')
        print(f"Setting {key} to {value} for bot {bot_id} at {timestamp}")
        # Set the control mode for the bot
        set_control_mode(bot_id, key, value)
            
    else:
        print(f"Unknown message type: {message_type}") 

def set_control_mode(bot_id, key, value):
    # Dummy function to set control mode, replace with actual implementation
    print(f"Control mode for {bot_id} set to {value}")  
   


def run_hardware_manager():
    global ws_stream
    global ws_messages
    global hardware_manager
    hardware_manager = HardwareManager()
    hardware_manager.start()
    ws_stream = WebsocketClass('localhost', 8765, start=True)
    ws_messages = WebsocketClass('localhost', 8766, start=True)
    ws_messages.set_message_callback(ws_callback)
    hardware_manager.registerCallback('stream', stream_callback)
    hardware_manager.registerCallback('robot_connected', new_robot)

    while True:
        time.sleep(1)


if __name__ == '__main__':
    run_hardware_manager()
