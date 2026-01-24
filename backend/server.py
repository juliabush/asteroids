import asyncio
import json
import websockets

from main import game_loop, create_world, world
from player import Player

connected_clients = set()
player_inputs = {}

KEY_MAP = {
    "ArrowUp": "up", "w": "up",
    "ArrowDown": "down", "s": "down",
    "ArrowLeft": "left", "a": "left",
    "ArrowRight": "right", "d": "right",
    " ": "space",
}

game_task = None


async def handler(websocket):
    global game_task

    connected_clients.add(websocket)

    p = Player(world["size"][0] / 2, world["size"][1] / 2)
    p.shot_cooldown = 0
    p.fire_held = False
    world["players"][websocket] = p

    player_inputs[websocket] = {
        "up": False,
        "down": False,
        "left": False,
        "right": False,
        "space": False,
    }

    if not game_task or game_task.done():
        game_task = asyncio.create_task(
            game_loop(connected_clients, player_inputs)
        )

    try:
        async for message in websocket:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type in ("input", "input_release"):
                key = data.get("key")
                if key in KEY_MAP:
                    player_inputs[websocket][KEY_MAP[key]] = (
                        msg_type == "input"
                    )

    except websockets.ConnectionClosed:
        pass
    finally:
        connected_clients.discard(websocket)
        world["players"].pop(websocket, None)
        player_inputs.pop(websocket, None)


async def main():
    create_world(640, 360)
    async with websockets.serve(handler, "0.0.0.0", 8000):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
