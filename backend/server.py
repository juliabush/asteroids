import asyncio
import json
import websockets
from datetime import datetime

connected_clients = set()

async def handler(websocket):
    connected_clients.add(websocket)
    print(f"Client connected ({len(connected_clients)} total)")

    try:
        await websocket.send(json.dumps({
            "type": "connection",
            "message": "Connected to Asteroids WebSocket server"
        }))

        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")

            response = {
                "type": "echo",
                "received": data,
                "timestamp": datetime.now().isoformat()
            }
            await asyncio.gather(
                *(client.send(json.dumps(response)) for client in connected_clients)
            )

    except websockets.ConnectionClosed:
        print("Client disconnected")
    finally:
        connected_clients.remove(websocket)
        print(f"Client removed ({len(connected_clients)} remaining)")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8000):
        print("WebSocket server running on ws://0.0.0.0:8000")
        await asyncio.Future()  

if __name__ == "__main__":
    asyncio.run(main())
