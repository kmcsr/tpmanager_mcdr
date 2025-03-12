
import mcdreforged.api.all as MCDR

from . import configs
from .utils import *
from . import commands as CMD
from . import api
from .api import *

__all__ = []

__all__.extend(api.__all__)

def on_load(server: MCDR.PluginServerInterface, prev_module):
	if prev_module is None:
		log_info('TP manager is on LOAD')
	else:
		log_info('TP manager is on RELOAD')
	configs.init(server)
	api.on_load(server, prev_module)
	CMD.register(server)

def on_unload(server: MCDR.PluginServerInterface):
	log_info('TP manager is on UNLOAD')
	api.on_unload(server)

def on_player_joined(server: MCDR.PluginServerInterface, player: str, info: MCDR.Info):
	api.on_player_joined(server, player, info)

def on_player_left(server: MCDR.PluginServerInterface, player: str):
	api.on_player_left(server, player)
