import asyncio as asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

import config

logger = logging.getLogger(__name__)


class PygbagnetManager:

    # Typing alias for an async event-handler
    _Handler = Callable[['PygbagnetManager', Any], Awaitable[None]]


    def __init__(self, node, poll_delay: float = 0.0) -> None:
        self.node = node
        self.poll_delay = poll_delay
        self.offers = dict()

        self._handlers: dict[Any, PygbagnetManager._Handler] = {
            node.CONNECTED: self._on_connected,
            node.JOINED: self._on_joined,
            node.GLOBAL: self._on_global,
            node.SPURIOUS: self._on_spurious,
            node.USERLIST: self._on_userlist,
            node.USERS: self._ignore,
            node.RAW: self._on_raw,
            node.B64JSON: self._on_b64json,
        }

    async def tick(self) -> None:
        for ev in self.node.get_events():
            try:
                await self._dispatch(ev)
            except Exception:
                logger.exception("Uncaught exception while handling %s (%s)", ev, self.node.data)

        await asyncio.sleep(0)

    async def _dispatch(self, ev) -> None:
        """Route an event to its dedicated handler."""
        handler = self._handlers.get(ev, self._on_unknown)
        await handler(ev)

    # ------------------- individual event handlers -------------------- #

    async def _on_connected(self, _) -> None:
        logger.info("CONNECTED as %s", self.node.nick)

    async def _on_joined(self, _) -> None:
        logger.info("Entered channel %s", self.node.current_channel)

    async def _on_global(self, _) -> None:
        # logger.debug("GLOBAL: %s", self.node.data)
        return

    async def _on_spurious(self, _) -> None:
        logger.debug("SPURIOUS: proto=%s data=%s", self.node.proto, self.node.data)

    async def _on_userlist(self, _) -> None:
        logger.debug("USERLIST: %s", self.node.users)

    async def _on_raw(self, _) -> None:
        logger.debug("RAW: %s", self.node.data)

    async def _on_b64json(self, ev) -> None:
        data = self.node.data

        if data['type'] == "offer":
            offer = data['offer']
            logger.info("Received offer: %s", offer)
            self.offers[offer['id']] = offer
        elif data['type'] == "join":
            logger.info(f"Received join: {data} -> {data['nick']}")
            config.gm.conn = data['nick']
            config.gm.send_full_data()
        elif data['type'] == 'message':
            logger.info(f"Received message: {data}")
            config.gm.process_network_message(data['message'])

        logger.debug("B64JSON: %s", data)

    async def _on_unknown(self, ev) -> None:
        logger.warning("Unhandled event: %s – rxq=%s", ev, self.node)

    async def _ignore(self, _) -> None:
        return

    def offer_lobby(self, lobby_id):
        offer = {'type': 'offer', 'offer': {'id': lobby_id,'lobby_name': config.pgnm.node.nick } }
        self.node.tx(offer)
        logger.info(f"Created lobby: {lobby_id}")

    def join_lobby(self, lobby: dict):
        logger.info(f"Connected to lobby: {lobby}")
        self.node.privmsg_b64json(lobby['lobby_name'], {'type': 'join', 'nick': config.pgnm.node.nick })
