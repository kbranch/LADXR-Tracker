import os
import asyncio
import requests
import traceback
import websockets
from gameboy import Gameboy
from items import *
from checks import *
from entrances import *
from romContents import *
from messages import *
from state import State

gb = Gameboy()

async def socketLoop(socket, path):
    print('Connected to tracker')

    state = State()
    loadItems(state)
    loadChecks(state)

    while True:
        await asyncio.sleep(0.4)

        if not gb.findEmulator():
            state.handshook = False
            continue

        if not state.entrancesLoaded and gb.canReadRom() and state.needsRom():
            romData = gb.readRom(0, 1024 * 1024)
            await state.parseRom(socket, romData)
            state.entrancesLoaded = True

        try:
            await state.processMessages(socket)

            gb.snapshot()

            gameState = gb.readRamByte(gameStateAddress)
            if gameState not in validGameStates:
                continue

            state.readTrackables(gb)
            
            if state.handshook:
                if not gb.canReadRom() and not state.romRequested and state.needsRom():
                    await sendRomRequest(socket)
                    state.romRequested = True

                await state.sendTrackables(socket)
        except Exception as e:
            print(f'Error: {traceback.format_exc()}')

def getRemoteVersion():
    try:
        request = requests.get('https://magpietracker.us/version')
        return json.loads(request.text)
    except:
        return None

def getVersion():
    try:
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'autotracker-version')
        with open(path, 'r') as reader:
            return reader.read().strip()
    except:
        return 'unknown'

async def main():
    version = getVersion()
    print(f'Autotracker version {version}, protocol {protocolVersion}')

    remote = getRemoteVersion()
    if remote:
        if remote['autotracker'] != version or remote['api'] != protocolVersion:
            print(f'Latest version is {remote["autotracker"]}, protocol {remote["api"]}')
        else:
            print("No update available")
    else:
        print("Unable to check for updates")

    print('\nListening for tracker')
    async with websockets.serve(socketLoop, host=None, port=17026, max_size=1024*1024*10):
        await asyncio.Future()

asyncio.run(main())