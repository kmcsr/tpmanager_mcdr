
from typing import Dict, List

import mcdreforged.api.all as MCDR

from kpi.config import Config
from .utils import *

__all__ = [
	'MSG_ID', 'BIG_BLOCK_BEFOR', 'BIG_BLOCK_AFTER', 'TPMConfig', 'get_config', 'init', 'destory'
]

MSG_ID = MCDR.RText('[TPM]', color=MCDR.RColor.light_purple)
BIG_BLOCK_BEFOR = LazyData(lambda data:
	MCDR.RText('------------ {0} v{1} ::::'.format(data.name, data.version), color=MCDR.RColor.gold))
BIG_BLOCK_AFTER = LazyData(lambda data:
	MCDR.RText(':::: {0} v{1} ============'.format(data.name, data.version), color=MCDR.RColor.gold))

class TPMConfig(Config, msg_id=MSG_ID):
	# 0:guest 1:user 2:helper 3:admin 4:owner
	minimum_permission_level: Dict[str, int] = {
		'help':    0,
		'pos':     2,
		'ask':     1,
		'askhere': 1,
		'accept':  1,
		'reject':  0,
	}
	teleport_expiration: int = 10 # in seconds
	teleport_commands: List[str] = [
		'say Teleporting {src} to {dst} ...',
		'tp {src} {dst}',
	]
	teleport_xyz_command: str = 'tp {name} {x} {y} {z}'

def get_config():
	return TPMConfig.instance

def init(server: MCDR.PluginServerInterface):
	global BIG_BLOCK_BEFOR, BIG_BLOCK_AFTER
	metadata = server.get_self_metadata()
	LazyData.load(BIG_BLOCK_BEFOR, metadata)
	LazyData.load(BIG_BLOCK_AFTER, metadata)
	TPMConfig.init_instance(server, load_after_init=True)

def destory(server: MCDR.PluginServerInterface):
	cfg = get_config()
	if cfg is not None:
		cfg.save()
