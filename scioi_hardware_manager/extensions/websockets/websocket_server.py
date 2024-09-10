import asyncio
import websockets
import json
import threading

class WebsocketClass:
    """
    The WebsocketClass manages a WebSocket server using asyncio and the websockets library.
    It facilitates communication between the TWIPR robot and a web interface, handling both
    incoming commands and outgoing data.
    """

    def __init__(self, host, port, start=False, recording: bool = False, recording_path: str = None):
        """
        Initializes the WebsocketClass with the specified host and port, and optionally starts
        the server. It also sets up recording options if needed.

        :param host: The hostname or IP address to bind the WebSocket server.
        :param port: The port number to bind the WebSocket server.
        :param start: A boolean flag to start the server immediately (default is False).
        :param recording: A boolean flag to enable or disable recording of WebSocket messages.
        :param recording_path: The path to save the recorded messages (default is None).
        """
        self.host = host
        self.port = port
        self.server = None
        self.clients = set()
        self.running = False
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start_loop)
        self.message_callback = None
        self.connection_callback = None
        self.recording = recording
        self.recording_path = recording_path

        if start:
            self.run()

    def _start_loop(self):
        """
        Internal method to initiate the event loop in a separate thread.
        """
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _handler(self, websocket, path):
        """
        Handles incoming WebSocket connections and messages. Manages the connected clients
        and processes messages using the provided callback functions.

        :param websocket: The WebSocket connection instance.
        :param path: The URL path of the WebSocket connection.
        """
        self.clients.add(websocket)
        if self.connection_callback:
            self.loop.call_soon_threadsafe(self.connection_callback, websocket)
        try:
            async for message in websocket:
                if self.message_callback:
                    self.loop.call_soon_threadsafe(self.message_callback, message)
                    # Record the received message if recording is enabled
                    if self.recording:
                        if isinstance(message, dict):
                            message_to_file = json.dumps(message)
                        else:
                            message_to_file = message
                        row = f"{time.time()},receive,{message_to_file}\n"
                        with open(self.recording_path, 'a') as file:
                            file.write(row)
        finally:
            self.clients.remove(websocket)

    async def _run_server(self):
        """
        Starts the WebSocket server and listens for incoming connections.
        """
        self.server = await websockets.serve(self._handler, self.host, self.port)
        self.running = True
        await self.server.wait_closed()

    def run(self):
        """
        Launches the WebSocket server in a separate thread if it is not already running.
        """
        if not self.running:
            self.thread.start()
            self.loop.call_soon_threadsafe(asyncio.create_task, self._run_server())

    async def _send(self, message):
        """
        Sends a message to all connected WebSocket clients. This method is asynchronous.

        :param message: The message to send to the clients. Can be a string or JSON-serializable dictionary.
        """
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])

    def send(self, message):
        """
        Sends a message to all connected clients. If the message is a dictionary, it is converted
        to a JSON string. Records the message if recording is enabled.

        :param message: The message to send. Can be a string or a dictionary.
        """
        if isinstance(message, dict):
            message = json.dumps(message)
        if self.recording:
            row = f"{time.time()},send,{message}\n"
            with open(self.recording_path, 'a') as file:
                file.write(row)
        asyncio.run_coroutine_threadsafe(self._send(message), self.loop)

    def stop(self):
        """
        Stops the WebSocket server and shuts down the event loop, cancelling all running tasks.
        """
        if self.running:
            for task in asyncio.all_tasks(loop=self.loop):
                task.cancel()
            self.loop.stop()
            self.server.close()
            self.running = False

    def set_message_callback(self, callback):
        """
        Sets the callback function to handle incoming WebSocket messages.

        :param callback: The function to call when a message is received.
        """
        self.message_callback = callback

    def set_connection_callback(self, callback):
        """
        Sets the callback function to handle new WebSocket connections.

        :param callback: The function to call when a new client connects.
        """
        self.connection_callback = callback
