#  WebsocketClass:

    The WebsocketClass manages a WebSocket server using asyncio and the websockets library.
    It facilitates communication between the TWIPR robot and a web interface, handling both
    incoming commands and outgoing data.
    

## Functions:

### privat __init__


        Initializes the WebsocketClass with the specified host and port, and optionally starts
        the server. It also sets up recording options if needed.

        

#### Parameters:

- **host:**  The hostname or IP address to bind the WebSocket server.
- **port:**  The port number to bind the WebSocket server.
- **start:**  A boolean flag to start the server immediately (default is False).
- **recording:**  A boolean flag to enable or disable recording of WebSocket messages.
- **recording_path:**  The path to save the recorded messages (default is None).

---
### privat _start_loop


        Internal method to initiate the event loop in a separate thread.
        


---
### privat _handler


        Handles incoming WebSocket connections and messages. Manages the connected clients
        and processes messages using the provided callback functions.

        

#### Parameters:

- **websocket:**  The WebSocket connection instance.
- **path:**  The URL path of the WebSocket connection.

---
### privat _run_server


        Starts the WebSocket server and listens for incoming connections.
        


---
### public run


        Launches the WebSocket server in a separate thread if it is not already running.
        


---
### privat _send


        Sends a message to all connected WebSocket clients. This method is asynchronous.

        

#### Parameters:

- **message:**  The message to send to the clients. Can be a string or JSON-serializable dictionary.

---
### public send


        Sends a message to all connected clients. If the message is a dictionary, it is converted
        to a JSON string. Records the message if recording is enabled.

        

#### Parameters:

- **message:**  The message to send. Can be a string or a dictionary.

---
### public stop


        Stops the WebSocket server and shuts down the event loop, cancelling all running tasks.
        


---
### public set_message_callback


        Sets the callback function to handle incoming WebSocket messages.

        

#### Parameters:

- **callback:**  The function to call when a message is received.

---
### public set_connection_callback


        Sets the callback function to handle new WebSocket connections.

        

#### Parameters:

- **callback:**  The function to call when a new client connects.

---
