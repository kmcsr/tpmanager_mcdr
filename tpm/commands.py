
import time
from typing import Callable, TypeVar

import mcdreforged.api.all as MCDR

from kpi.command import *

from .configs import *
from .utils import *
from .api import *

Prefix = '!!tp'
AlternativePrefix = '!!tpm'
TpaPrefix = '!!tpa'
TphPrefix = '!!tph'
WarpPrefix = '!!warp'

def register(server: MCDR.PluginServerInterface):
	cfg = get_config()
	points = WarpPoints.instance()
	assert points

	cmd = Commands(Prefix, config=cfg, points=points)
	cmd.register_to(server)

	server.register_command(
		MCDR.Literal(AlternativePrefix).redirects(cmd.node))

	server.register_command(
		require_player(
			cfg.require_permission(
				MCDR.Literal(TpaPrefix), 'ask')).
		redirects(Commands.ask.node))
	server.register_command(
		require_player(
			cfg.require_permission(
				MCDR.Literal(TphPrefix), 'askhere')).
			redirects(Commands.askhere.node))
	server.register_command(
		require_player(
			cfg.require_permission(
				MCDR.Literal(WarpPrefix), 'warp')).
			redirects(Commands.warp.node))
	server.register_help_message(TpaPrefix, 'Teleport to player')
	server.register_help_message(TphPrefix, 'Teleport player to you')
	server.register_help_message(WarpPrefix, 'Warp to warp point')

Self = TypeVar("Self", bound="Commands")

class Commands(PermCommandSet):
	Prefix = Prefix
	HelpMessage = 'TP manager help message'

	def __init__(self, *args, config: TPMConfig, points: WarpPoints, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = config
		self.__points = points
		self.__tpask_map: dict[str, tuple[Callable, Callable]] = {}
		self.__tpsender_map: dict[str, Callable] = {}
		self.__last_teleports: dict[str, float] = {}

	@property
	def config(self):
		return self.__config

	@property
	def points(self) -> WarpPoints:
		return self.__points

	def has_permission(self, src: MCDR.CommandSource, literal: str) -> bool:
		return self.config.has_permission(src, literal)

	def help(self, source: MCDR.CommandSource):
		send_message(source, BIG_BLOCK_BEFOR, tr('help_msg', Prefix, tpa=TpaPrefix, tph=TphPrefix), BIG_BLOCK_AFTER, sep='\n')

	@Literal('pos')
	@player_only
	def tppos(self, source: MCDR.PlayerCommandSource, x: float, y: float, z: float):
		server = source.get_server()
		player = source.player
		cooldown = self.config.teleport_cooldown
		if cooldown > 0:
			now = time.time()
			remain = self.__last_teleports.get(player, 0) + cooldown - now
			if remain > 0:
				send_message(source, MSG_ID, MCDR.RText(tr('ask.cooldown', round(remain)), color=MCDR.RColor.red))
				return
			self.__last_teleports[player] = now
		cmd = self.config.teleport_xyz_command.format(name=player, x=x, y=y, z=z)
		server.execute(cmd)

	@Literal('ask')
	@player_only
	def ask(self, source: MCDR.PlayerCommandSource, target: str):
		server = source.get_server()
		name = source.player
		if not is_online(target):
			send_message(source, MSG_ID, MCDR.RText(tr('ask.player_not_online', target), color=MCDR.RColor.yellow))
		if not self.register_accept(source, target,
			lambda: self.execute_teleport_commands(server, target, name),
			lambda: send_message(source, MSG_ID, MCDR.RText(tr('ask.aborted'), color=MCDR.RColor.red)),
			lambda: send_message(source, MSG_ID, MCDR.RText(tr('ask.timeout'), color=MCDR.RColor.red)),
			timeout=self.config.teleport_expiration):
			return
		send_message(source, MSG_ID, tr('ask.sending', target),
			new_command('{} cancel'.format(Prefix), '[{}]'.format(tr('word.cancel')), color=MCDR.RColor.yellow))
		server.tell(target, join_rtext(MSG_ID, tr('ask.request_to', name),
			new_command('{} accept'.format(Prefix), '[{}]'.format(tr('word.accept')), color=MCDR.RColor.light_purple),
			new_command('{} reject'.format(Prefix), '[{}]'.format(tr('word.reject')), color=MCDR.RColor.red),
		))

	def execute_teleport_commands(self, server: MCDR.ServerInterface, target: str, name: str):
		for c in self.config.teleport_commands:
			server.execute(c.format(src=name, dst=target))

	@Literal(['askhere', 'here'])
	@player_only
	def askhere(self, source: MCDR.PlayerCommandSource, target: str):
		server = source.get_server()
		name = source.player
		if not is_online(target):
			send_message(source, MSG_ID, MCDR.RText(tr('ask.player_not_online', target), color=MCDR.RColor.yellow))
		if not self.register_accept(source, target,
			lambda: self.execute_teleport_commands(server, name, target),
			lambda: send_message(source, MSG_ID, MCDR.RText(tr('ask.aborted'), color=MCDR.RColor.red)),
			lambda: send_message(source, MSG_ID, MCDR.RText(tr('ask.timeout'), color=MCDR.RColor.red)),
			timeout=self.config.teleport_expiration):
			return
		send_message(source, MSG_ID, tr('ask.sending', target),
			new_command('{} cancel'.format(Prefix), '[{}]'.format(tr('word.cancel')), color=MCDR.RColor.yellow))
		server.tell(target, join_rtext(MSG_ID, tr('ask.request_from', name),
			new_command('{} accept'.format(Prefix), '[{}]'.format(tr('word.accept')), color=MCDR.RColor.light_purple),
			new_command('{} reject'.format(Prefix), '[{}]'.format(tr('word.reject')), color=MCDR.RColor.red),
		))

	@Literal(['accept', 'acc'])
	@player_only
	def accept(self, source: MCDR.PlayerCommandSource):
		cbs = self.__tpask_map.pop(source.player.lower(), None)
		if cbs is None:
			send_message(source, MCDR.RText(tr('word.no_action'), color=MCDR.RColor.red))
			return
		cbs[0](source)

	@Literal(['reject', 'r'])
	@player_only
	def reject(self, source: MCDR.PlayerCommandSource):
		cbs = self.__tpask_map.pop(source.player.lower(), None)
		if cbs is None:
			send_message(source, MCDR.RText(tr('word.no_action'), color=MCDR.RColor.red))
			return
		cbs[1](source)

	@Literal(['cancel', 'c'])
	@player_only
	def cancel(self, source: MCDR.PlayerCommandSource):
		cb = self.__tpsender_map.pop(source.player.lower(), None)
		if cb is None:
			send_message(source, MCDR.RText(tr('word.no_action'), color=MCDR.RColor.red))
			return
		cb(source)

	def _has_warp_permission(self, source: MCDR.CommandSource, point: WarpPoint) -> bool:
		return source.has_permission(point.permission) or (isinstance(source, MCDR.PlayerCommandSource) and source.player.lower() == point.creator.lower())

	@Literal(['warp', 'w'])
	@player_only
	def warp(self, source: MCDR.PlayerCommandSource, name: str):
		server = source.get_server()
		if not self.config.enable_wrap:
			send_message(source, MCDR.RText(tr('warp.disabled'), color=MCDR.RColor.red))
			return
		point = self.points.get_point(name)
		if point is None:
			send_message(source, MCDR.RText(tr('warp.points.not_exists', name), color=MCDR.RColor.red))
			return
		if not self._has_warp_permission(source, point):
			send_message(source, MCDR.RText(tr('warp.points.no_permission'), color=MCDR.RColor.red))
			return
		send_message(source, MCDR.RText(tr('warp.teleporting', name=point.name), color=MCDR.RColor.light_purple))
		cmd = self.config.teleport_dim_xyz_command.format(name=source.player, x=point.x, y=point.y, z=point.z, dimension=point.dimension)
		server.execute(cmd)

	@Literal(['warps', 'ws'])
	class warps(PermCommandSet):
		def has_permission(self, src: MCDR.CommandSource, literal: str) -> bool:
			assert isinstance(self.rootset, Commands)
			return self.rootset.config.has_permission(src, 'warp_' + literal)

		def has_force_permission(self, src: MCDR.CommandSource) -> bool:
			assert isinstance(self.rootset, Commands)
			return self.rootset.config.has_permission(src, 'warp_config')

		@property
		def points(self) -> WarpPoints:
			assert isinstance(self.rootset, Commands)
			return self.rootset.points

		def _has_warp_permission(self, source: MCDR.CommandSource, point: WarpPoint) -> bool:
			assert isinstance(self.rootset, Commands)
			return self.rootset._has_warp_permission(source, point)

		def default(self, source: MCDR.CommandSource):
			self.list(self, source)

		@Literal(['list', 'l'])
		@call_with_root
		def list(self: Self, source: MCDR.CommandSource):
			points = [p for p in self.points.warp_points if self._has_warp_permission(source, p)]
			points.sort(key=lambda p: p.name.upper())
			send_message(source, BIG_BLOCK_BEFOR)
			for p in points:
				send_message(source, tr('warp.point', x=p.x, y=p.y, z=p.z, dimension=p.dimension, name=p.name))
			send_message(source, BIG_BLOCK_AFTER)

		@Literal(['set', 'add', 's'])
		def set(self, source: MCDR.CommandSource, name: str, x: float, y: float, z: float, dimension: str):
			server = source.get_server()
			# if x is None:
			# 	if not source.is_player:
			# 		send_message(source, MCDR.RText(server.rtr('kpi.command.player_only'), color=MCDR.RColor.red))
			# 		return
			# 	x, y, z = get_player_pos(source.player)
			point = self.points.get_point(name)
			if point is None:
				if self.points.points_count >= self.points.max_warp_points:
					send_message(source, MCDR.RText(tr('warp.points.full'), color=MCDR.RColor.red))
					return
				if isinstance(source, MCDR.PlayerCommandSource) and not self.has_force_permission(source):
					player_points_count = self.points.get_player_point_used(source.player)
					if player_points_count >= self.points.max_warp_points_per_player:
						send_message(source, MCDR.RText(tr('warp.points.full_per_player',
								count=player_points_count, limit=self.points.max_warp_points_per_player),
							color=MCDR.RColor.red))
						return
			elif not self._has_warp_permission(source, point) and not self.has_force_permission(source):
				send_message(source, MCDR.RText(tr('warp.points.exists'), color=MCDR.RColor.red))
				return
			self.points.set_point(WarpPoint(x=x, y=y, z=z, dimension=dimension, name=name,
				creator=source.player if isinstance(source, MCDR.PlayerCommandSource) else '',
				permission=1))
			send_message(source, MCDR.RText(tr('warp.created', name) if point is None else tr('warp.updated', point.name), color=MCDR.RColor.green), log=True)

		@Literal(['remove', 'r'])
		@call_with_root
		def remove(self: Self, source: MCDR.CommandSource, name: str):
			point = self.points.get_point(name)
			if point is None or not source.has_permission(point.permission):
				send_message(source, MCDR.RText(tr('warp.points.not_exists'), color=MCDR.RColor.red))
				return
			self.points.remove_point(point.name)
			send_message(source, MCDR.RText(tr('warp.removed', point.name), color=MCDR.RColor.gold), log=True)

	def register_accept(self, source: MCDR.PlayerCommandSource, target: str,
		accept_call, reject_call=None,
		timeout_call=None, timeout: int | None = None) -> bool:
		assert_instanceof(source, MCDR.PlayerCommandSource)
		assert callable(accept_call)
		assert reject_call is None or callable(reject_call)
		assert timeout_call is None or callable(timeout_call)
		if target.lower() in self.__tpask_map:
			send_message(source, MSG_ID, MCDR.RText(tr('ask.player_req_exists', target), color=MCDR.RColor.red))
			return False
		name = source.player
		if name.lower() in self.__tpsender_map:
			send_message(source, MSG_ID, MCDR.RText(tr('ask.req_exists'), color=MCDR.RColor.red))
			return False

		def timeout_cb():
			self.__tpask_map.pop(target.lower())
			self.__tpsender_map.pop(name.lower())
			if timeout_call is not None:
				timeout_call()
		timer = None if timeout is None else new_timer(timeout, timeout_cb)

		def accept_cb(*args):
			if timer is not None:
				timer.cancel()
			self.__tpsender_map.pop(name.lower())
			dyn_call(accept_call, *args)

		def reject_cb(*args):
			if timer is not None:
				timer.cancel()
			self.__tpsender_map.pop(name.lower())
			if reject_call is not None:
				dyn_call(reject_call, *args)

		def cancel_cb(*args):
			if timer is not None:
				timer.cancel()
			self.__tpask_map.pop(target.lower())
			if reject_call is not None:
				dyn_call(reject_call, *args)

		self.__tpask_map[target.lower()] = (accept_cb, reject_cb)
		self.__tpsender_map[name.lower()] = cancel_cb
		return True
