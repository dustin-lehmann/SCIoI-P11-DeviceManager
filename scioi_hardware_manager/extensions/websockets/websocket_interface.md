#  WebsocketInterface


    The WebsocketInterface class manages the communication between the robot manager and
    the clients connected through WebSocket. It handles incoming messages, manages joystick 
    connections, and relays streams and messages to the appropriate components.
    

## Functions:

### privat __init__


        Initializes the WebsocketInterface with the given WebSocket hosts and ports, and sets up
        the robot manager, joystick manager, and message handling.

        

#### Parameters:

- **stream_ws_host:**  Host for the stream WebSocket.
- **stream_ws_port:**  Port for the stream WebSocket.
- **message_ws_host:**  Host for the message WebSocket.
- **message_ws_port:**  Port for the message WebSocket.
- **robot_manager:**  An instance of RobotManager that manages connected robots.
- **logging:**  A boolean flag to enable or disable logging (errors are always logged).
- **recording:**  A boolean flag to enable or disable recording of WebSocket messages.
- **stream_recording_path:**  The path to save the recorded stream messages.
- **message_recording_path:**  The path to save the recorded message messages.

---
### public send_stream


        Sends the stream data through the stream WebSocket.

        

#### Parameters:

- **stream:**  The data stream to be sent.

---
### public send_message


        Sends a message through the message WebSocket.

        

#### Parameters:

- **message:**  The message to be sent.

---
### privat _message_callback


        Callback function that processes incoming messages and delegates them to the appropriate
        handler based on the message type.

        

#### Parameters:

- **message:**  The received message in JSON format.

---
### privat _command_message_handling


        Handles 'command' type messages. Processes the command or triggers emergency stop if necessary.

        

#### Parameters:

- **data:**  The data part of the message containing the command details.

---
### privat _joysticksChanged_message_handling


        Handles 'joysticksChanged' type messages. Updates the joystick assignments based on the data provided.

        

#### Parameters:

- **data:**  The data part of the message containing joystick details.

---
### privat _set_message_handling


        Handles 'set' type messages. Sets the control mode of the specified robot.

        

#### Parameters:

- **data:**  The data part of the message containing control mode details.

---
### privat _set_controller_parameters_message_handling


        Handles 'setControllerParameters' type messages. (Currently not implemented)

        

#### Parameters:

- **data:**  The data part of the message containing controller parameters.

---
### privat _robot_connect_callback


        Callback function that is triggered when a new robot is connected.
        Sends a notification message about the new robot connection.

        

#### Parameters:

- **robot:**  The connected robot instance.

---
### privat _robot_disconnect_callback


        Callback function that is triggered when a robot is disconnected.
        Sends a notification message about the robot disconnection.

        

#### Parameters:

- **robot:**  The disconnected robot instance.

---
### privat _joystick_connect_callback


        Callback function that is triggered when a new joystick is connected.
        Adds the joystick to the list and sends a notification message.

        

#### Parameters:

- **joystick:**  The connected joystick instance.

---
### privat _joystick_disconnect_callback


        Callback function that is triggered when a joystick is disconnected.
        Removes the joystick from the list and sends a notification message.

        

#### Parameters:

- **joystick:**  The disconnected joystick instance.

---
### privat _robot_stream_callback


        Callback function that is triggered when a robot sends a stream.
        Forwards the stream data to the appropriate WebSocket.

        

#### Parameters:

- **robot:**  The robot instance that is sending the stream.
- **stream:**  The stream data to be forwarded.

---
### privat _send_initial_values


        Sends the initial values to the connected client. This typically includes
        the current state of all joysticks. This function is called when a new 
        client connects or when the WebsocketInterface is initialized.
        


---
### privat _new_client_connected


        Callback function that is triggered when a new client connects to the message WebSocket.
        Sends the initial joystick values to the newly connected client.

        This ensures that the client is synchronized with the current state of the system
        as soon as the connection is established.
        


---
