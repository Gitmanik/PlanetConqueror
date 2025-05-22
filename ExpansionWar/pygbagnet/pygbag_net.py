import asyncio
import sys
import time
import select
import json
import base64
import io
import traceback
import socket

class WebsocketWrapper:
    def __init__(self):
        import websockets
        self._websocket : websockets.ClientConnection = None
        self.recv_buffer = b''

    async def connect(self, host, port):
        import websockets
        ws_url = f"ws://{host}:{port}"
        self._websocket = await websockets.connect(ws_url)

    async def send(self, data):
        await self._websocket.send(data)

    async def close(self):
        await self._websocket.close()

    def recv(self, size, t):
        ret = self.recv_buffer[0].to_bytes()
        self.recv_buffer = self.recv_buffer[1:]
        return ret

    async def select(self):
        if len(self.recv_buffer) == 0:
            self.recv_buffer += await self._websocket.recv()
        return len(self.recv_buffer), None, None

async def aio_sock_open(sock, host, port):
    if sys.platform != "emscripten":
        try:
            await sock.connect(host, port)
            return sock
        except Exception as e:
            traceback.print_exception(e)
            return None
    else:
        while True:
            try:
                sock.connect((host, port))
            except BlockingIOError:
                await asyncio.sleep(0)
            except OSError as e:
                if e.errno in (30, 106):
                    return sock
                traceback.print_exception(e)



class aio_sock:
    def __init__(self, url, mode, tmout):
        host, port = url.rsplit(":", 1)
        self.port = int(port)
        _, host = host.split("://", 1)
        self.host = host

        self.socket = socket.socket() if sys.platform == "emscripten" else WebsocketWrapper()

        print(f"host={host} port={port} mode={mode} tmout={tmout}")

    def fileno(self):
        return self.socket.fileno() if sys.platform == "emscripten" else None

    async def send(self, data):
        data = data.encode('utf-8') if isinstance(data, str) else data
        if sys.platform != "emscripten":
            await self.socket.send(data)
        else:
            self.socket.send(data)

    async def recv(self, size=-1, t = None):
        return self.socket.recv(size, t)

    async def __aenter__(self):
        await aio_sock_open(self.socket, self.host, self.port)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if sys.platform != "emscripten":
            await self.socket.close()
        del self.port, self.host, self.socket

    def print(self, *argv, **kw):
        kw["file"] = io.StringIO(newline="\r\n")
        print(*argv, **kw)
        asyncio.create_task(self.send(kw["file"].getvalue()))


class Node:
    CONNECTED = "a"
    RX = "b"
    PING = "c"
    PONG = "d"
    RAW = "e"
    USERS = "i"
    SPURIOUS = "j"
    GLOBAL = "k"
    USERLIST = "l"
    JOINED = "m"
    B64JSON = "j64"

    host = "://pmp-p.ddns.net/wss/6667:443"
    lobby = "#pygbag"

    events = []

    def __init__(self, gid):
        self.aiosock = None

        self.gid = gid
        Node.lobby_channel = f"{Node.lobby}-{gid}"
        self.lobby_channel = Node.lobby_channel

        self.users = {}

        self.rxq = []
        self.txq = []
        self.alarm_set = 0

        self.current_channel = ""

        asyncio.create_task(self.connect(Node.host))

        stime = str(time.time())[-5:].replace(".", "")
        self.pid = int(stime)
        self.nick = f"u_{self.pid}"

    async def connect(self, host):
        self.peek = []
        async with aio_sock(host, "a+", 5) as sock:
            self.host = host
            self.events.append(self.CONNECTED)
            self.aiosock = sock

            while True:
                if sys.platform == 'emscripten':
                    rr, rw, re = select.select([sock.socket], [], [], 0)
                else:
                    rr, rw, re = await sock.socket.select()
                if rr or rw or re:
                    while self.aiosock:
                        try:
                            one = await sock.recv(1, socket.MSG_DONTWAIT)
                            if one:
                                self.peek.append(one)
                                if one == b"\n":
                                    self.rxq.append(b"".join(self.peek))
                                    self.peek.clear()
                                    self.events.append(self.RX)
                                    break
                            else:
                                # lost con.
                                print("HANGUP", self.peek)
                                self.aiosock = None
                                print("TODO: ask for reconnect")
                                return
                        except BlockingIOError as e:
                            if e.errno == 6:
                                await asyncio.sleep(0)
                else:
                    await asyncio.sleep(0)

    def tx(self, obj):
        ser = json.dumps(obj)
        self.out(self.B64JSON + ":" + base64.b64encode(ser.encode("ascii")).decode("utf-8"))

    def join(self, channel):
        self.wire(f"JOIN {channel}")

    def privmsg(self, nick, data):
        self.wire(f"PRIVMSG {nick} :{data}")

    def privmsg_b64json(self, nick, data):
        ser = json.dumps(data)
        self.privmsg(nick, f"{self.B64JSON}:{base64.b64encode(ser.encode('ascii')).decode('utf-8')}")

    def out(self, *blocks):
        self.privmsg(self.lobby_channel, ' '.join(map(str, blocks)))

    # TODO: handle hangup/reconnect nicely (no flood)
    def wire(self, rawcmd):
        self.txq.append(rawcmd)
        if self.aiosock and self.aiosock.socket:
            while len(self.txq):
                self.aiosock.print(self.txq.pop(0))

    def process_server(self, cmd, line):
        self.discarded = False

        if cmd.find(" 353 ") > 0:
            self.proto = "users"
            self.data = line.split(" ")
            for u in self.data:
                if not u in self.users:
                    self.users.setdefault(u, {})

            yield self.USERS
            return self.discard()

        if cmd.find(" 332 ") > 0:
            yield self.SPURIOUS
            return self.discard()

        if cmd.find(" 331 ") > 0:
            yield self.SPURIOUS
            return self.discard()

        if cmd.find(" 366 ") > 0:
            yield self.USERLIST
            return self.discard()

        if cmd.find(" JOIN #") > 0:
            self.proto = "join"
            self.current_channel = cmd.split(" JOIN ")[-1]
            self.data = self.current_channel
            self.users = {}

            yield self.JOINED
            return self.discard()

        if cmd.find(" PONG ") > 0:
            self.proto, self.data = cmd.strip().split(" PONG ", 1)
            yield self.PONG
            return self.discard()

        for srv in "001 002 003 004 251 375 372 376".split(" "):
            if cmd.find(f" {srv} ") > 0:
                self.proto = cmd
                self.data = line.strip()
                yield self.GLOBAL
                return self.discard()

        if cmd.find("PING ") >= 0:
            print("348: PING ?")
            self.proto, self.data = cmd.strip().split(":", 1)
            self.wire(line.replace("PING ", "PONG ", 1))
            yield self.PING
            return self.discard()

    def process_game(self, cmd, line):
        self.discarded = False

        if line.startswith(f"{Node.B64JSON}:"):
            try:
                _, data = line.split(":", 1)
                data = base64.b64decode(data.encode())
                self.data = json.loads(data.decode())
                yield self.B64JSON
                return self.discard()

            except Exception as e:
                traceback.print_exception(e)

    def discard(self):
        self.discarded = True

    def get_events(self):
        while len(self.events):
            ev = self.events.pop(0)

            if ev == self.RX:
                while len(self.rxq):
                    srvdata = self.rxq.pop(0).decode("utf-8").strip().split(":", 2)
                    noise = srvdata.pop(0)
                    if noise:
                        print(f"364: server {noise=} on rxq, remaining {srvdata=}")

                    if len(srvdata) < 2:
                        srvdata.append("")

                    yield from self.process_server(*srvdata)

                    if not self.discarded:
                        yield from self.process_game(*srvdata)

                    if not self.discarded:
                        self.data = ":".join(srvdata)
                        yield self.RAW
                continue

            if ev == self.CONNECTED:
                self.wire(f"CAP LS\r\nNICK {self.nick}\r\nUSER {self.nick} {self.nick} localhost :wsocket")
                self.join(self.lobby_channel)
            else:
                print(f"402:? {ev=} {self.rxq=}")

            yield ev
