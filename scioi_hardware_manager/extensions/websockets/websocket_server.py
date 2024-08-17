import asyncio
import websockets
import json
import threading

class WebsocketClass:
    """
    A class to manage a WebSocket server using asyncio and websockets library.
    It is used to send data from the TWIPR robot to the web interface and to receive and process commands from the web interface.

    Attributes:
    host : str
        The hostname or IP address to bind the WebSocket server.
    port : int
        The port number to bind the WebSocket server.
    server : websockets.server.WebSocketServer
        The WebSocket server instance.
    clients : set
        A set of connected WebSocket clients.
    running : bool
        A flag indicating if the server is currently running.
    loop : asyncio.AbstractEventLoop
        The event loop running the WebSocket server.
    thread : threading.Thread
        A separate thread to run the event loop.
    message_callback : callable
        A callback function to handle incoming messages.
    connection_callback : callable
        A callback function to handle new connections.
    """

    def __init__(self, host, port, start=False):
        """
        Initializes the WebSocket server with the given host and port.
        
        Parameters:
        host : str
            The hostname or IP address to bind the WebSocket server.
        port : int
            The port number to bind the WebSocket server.
        start : bool, optional
            If True, starts the server immediately (default is False).
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

        if start:
            self.run()

    def _start_loop(self):
        """
        Internal method to start the event loop in a separate thread.
        """
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _handler(self, websocket, path):
        """
        Internal method to handle incoming WebSocket connections and messages.
        
        Parameters:
        websocket : websockets.WebSocketServerProtocol
            The WebSocket connection instance.
        path : str
            The URL path of the WebSocket connection.
        """
        self.clients.add(websocket)
        if self.connection_callback:
            self.loop.call_soon_threadsafe(self.connection_callback, websocket)
        try:
            async for message in websocket:
                if self.message_callback:
                    self.loop.call_soon_threadsafe(self.message_callback, message)
        finally:
            self.clients.remove(websocket)

    async def _run_server(self):
        """
        Internal method to start the WebSocket server and wait for connections.
        """
        self.server = await websockets.serve(self._handler, self.host, self.port)
        self.running = True
        await self.server.wait_closed()

    def run(self):
        """
        Starts the WebSocket server in a separate thread if it is not already running.
        """
        if not self.running:
            self.thread.start()
            self.loop.call_soon_threadsafe(asyncio.create_task, self._run_server())

    async def _send(self, message):
        """
        Internal method to send a message to all connected clients.
        
        Parameters:
        message : str
            The message to send to the clients.
        """
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])

    def send(self, message):
        """
        Sends a message to all connected clients. The message can be a dictionary or string.

        Parameters:
        message : str or dict
            The message to send. If it's a dictionary, it will be converted to a JSON string.
        """
        if isinstance(message, dict):
            message = json.dumps(message)
        asyncio.run_coroutine_threadsafe(self._send(message), self.loop)

    def stop(self):
        """
        Stops the WebSocket server and shuts down the event loop.
        """
        if self.running:
            for task in asyncio.all_tasks(loop=self.loop):
                task.cancel()
            self.loop.stop()
            self.server.close()
            self.running = False

    def set_message_callback(self, callback):
        """
        Sets the callback function to handle incoming messages.
        
        Parameters:
        callback : callable
            The function to call when a message is received.
        """
        self.message_callback = callback

    def set_connection_callback(self, callback):
        """
        Sets the callback function to handle new connections.
        
        Parameters:
        callback : callable
            The function to call when a new client connects.
        """
        self.connection_callback = callback
