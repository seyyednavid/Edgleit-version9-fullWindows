"""
WebSocket Module

This module handles WebSocket connections and communication with clients.
It defines functions to handle client connections, process messages,
and manage the WebSocket server thread.
"""

from appContents import app
from appContents.models import Settings
import json
import websockets
import threading
import asyncio
import os


# Variable to store number of cashiers (0-23)
called_position = 0

# Store a set of connected websocket clients
connected_clients = set()


async def hex_to_rgb(hex):
    """Convert hexadecimal color code to RGB tuple."""
    return tuple(int(hex[i:i+2], 16) for i in (1, 3, 5))

"""Handle WebSocket client connections and messages."""
async def handle_client(websocket, path):
    global called_position
    # Add the client to the set of connected clients
    connected_clients.add(websocket)
    print(f"New client connected. Total clients: {len(connected_clients)}")

    try:
        while True:
            # Wait for a message from the client
            message_json = await websocket.recv()  

            if message_json:
                # Parse JSON message
                try:
                    message_data = json.loads(message_json)
                    print("------------------------------------------------------------------",message_data)

                    if message_data["ws_id"] == "Tensator_Websocket_server":
                        if message_data["cb_id"] == "CB_123456789":
                            if message_data["device_type"] == "Edgelit-button":
                                egdelit_id = int(message_data["cmd_info"]["target"])
                                called_position = egdelit_id
                                event = message_data["cmd_info"]["event"]

                                with app.app_context():
                                    data_in_db = Settings.query.filter_by(id=egdelit_id).first()

                                    if data_in_db:
                                        message_data["cmd_info"]["flash_speed"] = int(data_in_db.flashspeededgelit)
                                        message_data["cmd_info"]["no_of_flashes"] = int(data_in_db.numofflashes)
                                        message_data["cmd_info"]["on_color"] = await hex_to_rgb(data_in_db.on_color)
                                        message_data["cmd_info"]["off_color"] = await hex_to_rgb(data_in_db.off_color)
                                        message_data["cmd_info"]["free_color"] = await hex_to_rgb(data_in_db.free_color)
                                        message_data["cmd_info"]["busy_color"] = await hex_to_rgb(data_in_db.busy_color)
                                        print(f"\nthe message prepared to be sent: {message_data}\n")
                                        # Send message to all connected clients
                                        for client in connected_clients:
                                            await client.send(json.dumps(message_data))
                                    else:
                                        print(f"No data found in the database for edgelit_id: {egdelit_id}")
                            else:
                                print("type mismatch")
                        else:
                            print("cb_id mismatch")
                    else:
                        print("ws_id mismatch")

                except json.JSONDecodeError:
                    print("Error decoding JSON message")

    except websockets.exceptions.ConnectionClosed:
        connected_clients.remove(websocket)
        print(f"Client {websocket} disconnected. Total clients: {len(connected_clients)}")


class WebSocketServerThread(threading.Thread):
    """Manage the WebSocket server thread."""
    def __init__(self):
        super().__init__()
        self.running = True
        self.server = None  # Variable to store the server instanc
        self.serve_forever_task = None  #  Variable to store the serve_forever task

    def terminate(self):
        """Terminate the WebSocket server thread."""
        self.running = False
        if self.server:
            # Close the server
            self.server.close() 
            asyncio.run_coroutine_threadsafe(self.serve_forever_task.cancel(), asyncio.get_event_loop())
            asyncio.get_event_loop().run_until_complete(self.server.wait_closed())  # Wait for server to close

    def run(self):
        """Run the WebSocket server."""
        while self.running:
            asyncio.set_event_loop(asyncio.new_event_loop())
            self.server = websockets.serve(handle_client, os.getenv("FLASK_IP_ADDRESS"),os.getenv("WEBSOCKET_PORT"))
            self.serve_forever_task = asyncio.ensure_future(self.server)
            asyncio.get_event_loop().run_until_complete(self.serve_forever_task)
            asyncio.get_event_loop().run_forever()