import asyncio
import websockets
import json
import os

rooms = {}   # passcode -> set of websockets

async def handler(ws):
    room = None
    try:
        async for msg in ws:
            data = json.loads(msg)

            # first message must be join
            if data["type"] == "join":
                room = data["room"]

                if room not in rooms:
                    rooms[room] = set()

                rooms[room].add(ws)
                continue

            if data["type"] == "chat":
                if room is None:
                    continue

                for client in list(rooms.get(room, [])):
                    if client.open:
                        await client.send(msg)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if room and room in rooms:
            rooms[room].discard(ws)
            if not rooms[room]:
                del rooms[room]


async def main():
    port = int(os.environ.get("PORT", 8000))
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
