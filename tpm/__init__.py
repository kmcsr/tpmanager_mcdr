
import mcdreforged.api.all as MCDR

globals_ = globals
from . import globals as GL
from .utils import *
from . import commands as CMD
from . import api

__all__ = []

__all__.extend(api.__all__)

def on_load(server: MCDR.PluginServerInterface, prev_module):
	if prev_module is None:
		log_info('TP manager is on LOAD')
	else:
		log_info('TP manager is on RELOAD')
	GL.init(server)
	api.on_load(server, prev_module)
	CMD.register(server)

def on_unload(server: MCDR.PluginServerInterface):
	log_info('TP manager is on UNLOAD')
	api.on_unload(server)
	GL.destory(server)
