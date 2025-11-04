# server.py — System audio capture + WS stream + HTTP UI (multi-client safe)
import socket, sys, asyncio, struct
from threading import Thread
from flask import Flask, send_from_directory
import sounddevice as sd
import websockets

SAMPLE_RATE = 44100
CHANNELS = 2
BLOCK = 1024
PORT_HTTP = 5000
PORT_WS   = 8765

# ------------------ HTTP SERVER ------------------
app = Flask(__name__)
@app.route('/')
def index():
    return send_from_directory('.', 'client.html')

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "127.0.0.1"
    finally:
        s.close()

HOST = get_ip()

# ------------------ AUDIO DEVICE PICK ------------------
def list_devs():
    devs = sd.query_devices()
    print("\n--- Devices ---")
    for i, d in enumerate(devs):
        print(i, d['name'], "| out:", d['max_output_channels'], "in:", d['max_input_channels'])
    return devs

def try_wasapi(idx):
    try:
        print(f"Trying WASAPI loopback on {idx}")
        try:
            ws = sd.WasapiSettings(loopback=True)
        except:
            ws = None
        stream = sd.InputStream(
            device=idx, samplerate=SAMPLE_RATE,
            channels=CHANNELS, blocksize=BLOCK,
            dtype="int16", extra_settings=ws
        )
        stream.start()
        print("WASAPI loopback success", idx)
        return stream
    except Exception as e:
        print(f"failed WASAPI {idx}: {e}")
        return None

def try_stereo_mix(candidates):
    for idx in candidates:
        try:
            print("Trying Stereo Mix", idx)
            stream = sd.InputStream(
                device=idx, samplerate=SAMPLE_RATE,
                channels=CHANNELS, blocksize=BLOCK, dtype="int16"
            )
            stream.start()
            print("Stereo Mix OK", idx)
            return stream
        except:
            pass
    return None

devs = list_devs()
out_candidates = [i for i,d in enumerate(devs) if d['max_output_channels']>0]
stereo_candidates = [i for i,d in enumerate(devs) if "stereo" in d['name'].lower() or d['max_input_channels']>0]

stream = None
for idx in out_candidates:
    stream = try_wasapi(idx)
    if stream: break

if not stream:
    print("\nLoopback failed → trying Stereo Mix fallback")
    stream = try_stereo_mix(stereo_candidates)

if not stream:
    print("No audio source found. Enable Stereo Mix or WASAPI loopback in Windows sound.")
    sys.exit(1)

# ------------------ MULTI-CLIENT WS STREAM ------------------
clients = set()

async def audio_broadcast():
    """Continuously capture system audio once and send to all clients."""
    while True:
        frames, _ = stream.read(BLOCK)
        raw = frames.tobytes()

        for ws in list(clients):
            try:
                await ws.send(raw)
            except:
                clients.discard(ws)

        await asyncio.sleep(0)  # let event loop breathe

async def ws_handler(websocket):
    """Client connects – add to client set"""
    clients.add(websocket)
    print("Client connected:", websocket.remote_address)
    try:
        await asyncio.Future()  # keep open
    except:
        pass
    print("Client disconnected:", websocket.remote_address)
    clients.discard(websocket)

async def ws_main():
    print(f"WS: ws://{HOST}:{PORT_WS}")
    server = websockets.serve(ws_handler, "0.0.0.0", PORT_WS, max_size=None)
    await asyncio.gather(server, audio_broadcast())

def http_start():
    print(f"HTTP: http://{HOST}:{PORT_HTTP}")
    app.run(host="0.0.0.0", port=PORT_HTTP)

# ------------------ START ------------------
if __name__ == "__main__":
    Thread(target=http_start, daemon=True).start()
    asyncio.run(ws_main())
