import asyncio as aio
import traceback

class PygbagnetManager:

    def __init__(self, node):
        self.node = node

    async def tick(self):
        for ev in self.node.get_events():
            try:
                if ev == self.node.SYNC:
                    cmd = self.node.data[self.node.CMD]
                    print("SYNC:", self.node.proto, self.node.data, cmd)
    
                elif ev == self.node.GAME:
                    cmd = self.node.data[self.node.CMD]
                    print("GAME:", self.node.proto, self.node.data, cmd)
    
                    if cmd == "clone":
                        # send all history to child
                        self.node.checkout_for(self.node.data)
    
                    elif cmd == "ingame":
                        print("TODO: join game")
                    else:
                        print("602 ?", cmd, self.node.data)
    
                elif ev == self.node.CONNECTED:
                    print(f"CONNECTED as {self.node.nick}")
    
                elif ev == self.node.JOINED:
                    print("Entered channel", self.node.joined)
                    if self.node.joined == self.node.lobby_channel:
                        self.node.tx({self.node.CMD: "ingame", self.node.PID: self.node.pid})
    
                elif ev == self.node.TOPIC:
                    print(f'[{self.node.channel}] TOPIC "{self.node.topics[self.node.channel]}"')
    
                elif ev in [self.node.LOBBY, self.node.LOBBY_GAME]:
                    cmd, pid, nick, info = self.node.proto
    
                    if cmd == self.node.HELLO:
                        print("Lobby/Game:", "Welcome", nick)
                        # publish if main
                        if not self.node.fork:
                            self.node.publish()
    
                    elif (ev == self.node.LOBBY_GAME) and (cmd == self.node.OFFER):
                        if self.node.fork:
                            print("cannot fork, already a clone/fork pid=", self.node.fork)
                        elif len(self.node.pstree[self.node.pid]["forks"]):
                            print("cannot fork, i'm main for", self.node.pstree[self.node.pid]["forks"])
                        else:
                            print("forking to game offer", self.node.hint)
                            self.node.clone(pid)
    
                    else:
                        print(f"\nLOBBY/GAME: {self.node.fork=} {self.node.proto=} {self.node.data=} {self.node.hint=}")
    
                elif ev in [self.node.USERS]:
                    ...
    
                elif ev in [self.node.GLOBAL]:
                    print("GLOBAL:", self.node.data)
    
                elif ev in [self.node.SPURIOUS]:
                    print(f"\nRAW: {self.node.proto=} {self.node.data=}")
    
                elif ev in [self.node.USERLIST]:
                    print(self.node.proto, self.node.users)
    
                elif ev == self.node.RAW:
                    print("RAW:", self.node.data)
    
                elif ev == self.node.PING:
                    # print("ping", self.node.data)
                    ...
                elif ev == self.node.PONG:
                    # print("pong", self.node.data)
                    ...
    
                # promisc mode dumps everything.
                elif ev == self.node.RX:
                    ...
    
                else:
                    print(f"52:{ev=} {self.node.rxq=}")
            except Exception as e:
                print(f"52:{ev=} {self.node.rxq=} {self.node.proto=} {self.node.data=}")
                traceback.print_exception(e)
    
        await aio.sleep(0)