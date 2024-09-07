
import mcdreforged.api.all as MCDR

from .utils import *

__all__ = [
	'is_online'
]

players = set()

def on_load(server: MCDR.PluginServerInterface, prev_module):
	if prev_module is not None and prev_module.api is not None:
		if isinstance(prev_module.api.players, set):
			players = prev_module.api.players

def on_unload(server: MCDR.PluginServerInterface):
	pass

def on_player_joined(server: MCDR.PluginServerInterface, player: str, info: MCDR.Info):
	players.add(player.lower())

def on_player_left(server: MCDR.PluginServerInterface, player: str):
	players.remove(player.lower())

def is_online(player: str) -> bool:
	return player.lower() in players
