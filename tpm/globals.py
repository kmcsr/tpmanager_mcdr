
from typing import Dict, List

import mcdreforged.api.all as MCDR

from kpi.config import *
from kpi.utils import LazyData
from .utils import *

__all__ = [
	'MSG_ID', 'BIG_BLOCK_BEFOR', 'BIG_BLOCK_AFTER',
	'TPMConfig', 'get_config',
	'WarpPoint', 'WarpPoints',
	'init', 'destory'
]

MSG_ID = MCDR.RText('[TPM]', color=MCDR.RColor.light_purple)
BIG_BLOCK_BEFOR = LazyData(lambda data:
	MCDR.RText('------------ {0} v{1} ::::'.format(data.name, data.version), color=MCDR.RColor.gold))
BIG_BLOCK_AFTER = LazyData(lambda data:
	MCDR.RText(':::: {0} v{1} ============'.format(data.name, data.version), color=MCDR.RColor.gold))

class TPMConfig(Config, msg_id=MSG_ID):
	# 0:guest 1:user 2:helper 3:admin 4:owner
	class minimum_permission_level(JSONObject):
		pos: int     = 2
		ask: int     = 1
		askhere: int = 1
		accept: int  = 1
		reject: int  = 0
		cancel: int  = 0
		warp: int = 1
		warp_set: int = 2
		warp_remove: int = 2
		warp_config: int = 3

	teleport_cooldown: int = 60 # in seconds
	teleport_expiration: int = 10 # in seconds
	teleport_commands: List[str] = [
		'say Teleporting {src} to {dst} ...',
		'tp {src} {dst}',
	]
	teleport_xyz_command: str = 'tp {name} {x} {y} {z}'
	teleport_dim_xyz_command: str = 'execute in {dimension} run tp {name} {x} {y} {z}'
	enable_wrap: bool = True

class WarpPoint(JSONObject):
	x: float
	y: float
	z: float
	dimension: str
	creator: str
	name: str
	permission: int = 1

class WarpPoints(JSONStorage):
	_instance: ClassVar[Optional[Self]] = None

	max_warp_points: int = 9 # or -1 means no limit
	warp_points: List[WarpPoint] = []

	@classmethod
	def instance(cls) -> Optional[Self]:
		return cls._instance

	@property
	def points_count(self) -> int:
		return len(self.warp_points)

	def get_point(self, name: str) -> WarpPoint | None:
		name = name.lower()
		for p in self.warp_points:
			if p.name.lower() == name:
				return p
		return None

	def set_point(self, point: WarpPoint):
		name = point.name.lower()
		for i, p in enumerate(self.warp_points):
			if p.name.lower() == name:
				self.warp_points[i] = point
		self.warp_points.append(point)

	def remove_point(self, name: str) -> WarpPoint | None:
		name = name.lower()
		for i, p in enumerate(self.warp_points):
			if p.name.lower() == name:
				self.warp_points.pop(i)
				return p
		return None

def get_config():
	return TPMConfig.instance

def init(server: MCDR.PluginServerInterface):
	global BIG_BLOCK_BEFOR, BIG_BLOCK_AFTER
	metadata = server.get_self_metadata()
	LazyData.load(BIG_BLOCK_BEFOR, metadata)
	LazyData.load(BIG_BLOCK_AFTER, metadata)
	TPMConfig.init_instance(server, load_after_init=True).save()
	WarpPoints._instance = WarpPoints(server, 'points.json', sync_update=True, load_after_init=True)

def destory(server: MCDR.PluginServerInterface):
	pass
