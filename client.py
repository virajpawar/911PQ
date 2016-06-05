#!/usr/bin/env python

import asyncio
import websockets

async def handler():
    async with websockets.connect('ws://0.0.0.0:23456') as websocket:
        while True:
            message = await websocket.recv()
            print("< {}".format(message))
            print()

loop = asyncio.get_event_loop()
loop.run_until_complete(handler())
loop.run_forever()
