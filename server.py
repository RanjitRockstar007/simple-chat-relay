import asyncio
import websockets
import json
import os

rooms = {}

async def handler(ws):
    room = None
    print("Client connected")

    try:
        async for msg in ws:
            print("Received raw:", msg)

            data = json.loads(msg)

            if data["type"] == "join":
                room = data["room"]

                if room not in rooms:
                    rooms[room] = set()

                rooms[room].add(ws)

                print("Client joined room:", room, "count:", len(rooms[room]))
                continue

            if data["type"] == "chat":
                print("Broadcasting to room:", room)

                dead = []

                for client in rooms.get(room, set()):
                    try:
                        await client.send(msg)
                    except:
                        dead.append(client)

                for d in dead:
                    rooms[room].discard(d)

    except Exception as e:
        print("Handler error:", e)

    finally:
        print("Client disconnected")

        if room and room in rooms:
            rooms[room].discard(ws)
            if not rooms[room]:
                del rooms[room]


async def main():
    port = int(os.environ.get("PORT", 8000))

    async with websockets.serve(handler, "0.0.0.0", port):
        print("WebSocket relay running on port", port)
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
