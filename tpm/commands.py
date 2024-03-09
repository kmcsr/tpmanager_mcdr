
import mcdreforged.api.all as MCDR

import time

from kpi.command import *

from .globals import *
from .utils import *
from .api import *

Prefix = '!!tp'
TpaPrefix = '!!tpa'
TphPrefix = '!!tph'

def register(server: MCDR.PluginServerInterface):
	cfg = get_config()

	Commands(Prefix, config=cfg).register_to(server)

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
	server.register_help_message(TpaPrefix, 'Teleport to player')
	server.register_help_message(TphPrefix, 'Teleport player to you')

class Commands(PermCommandSet):
	Prefix = Prefix
	HelpMessage = 'TP manager help message'

	def __init__(self, *args, config, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = config
		self.__tpask_map = {}
		self.__tpsender_map = {}
		self.__last_teleports: dict[str, float] = {}

	@property
	def config(self):
		return self.__config

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
		# TODO: check the target player exists
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
		# TODO: check the target player exists
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
