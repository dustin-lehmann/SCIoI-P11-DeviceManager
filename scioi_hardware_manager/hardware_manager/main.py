import time

from hardware_manager.manager import HardwareManager
from hardware_manager.helper.websocket_server import WebsocketClass
ws_stream = None
ws_messages = None


def stream_callback(stream, device, *args, **kwargs):
    global ws_stream
    ws_stream.send(stream)
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

def websocket_callback(message):
    print(f"Received message: {message}")

def run_hardware_manager():
    global ws_stream
    global ws_messages
    hardware_manager = HardwareManager()
    hardware_manager.start()
    ws_stream = WebsocketClass('localhost', 8765, start=True)
    ws_messages = WebsocketClass('localhost', 8766, start=True)
    ws_messages.set_message_callback(websocket_callback)
    hardware_manager.registerCallback('stream', stream_callback)
    hardware_manager.registerCallback('robot_connected', new_robot)

    while True:
        time.sleep(1)


if __name__ == '__main__':
    run_hardware_manager()
