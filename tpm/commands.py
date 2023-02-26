
import mcdreforged.api.all as MCDR

from kpi.command import *

from .globals import *
from .utils import *
from .api import *

Prefix = '!!tp'
TpaPrefix = '!!tpa'
TphPrefix = '!!tph'

def register(server: MCDR.PluginServerInterface):
	cfg = get_config()
	server.register_help_message(Prefix, 'TP manager help message')
	server.register_help_message(TpaPrefix, 'Teleport to player')
	server.register_help_message(TphPrefix, 'Teleport player to you')

	Commands(Prefix, config=cfg).register_to(server)

	server.register_command(
		require_player(
			cfg.require_permission(
				MCDR.Literal(TpaPrefix), 'ask')).
		redirects(Commands.ask.base))
	server.register_command(
		require_player(
			cfg.require_permission(
				MCDR.Literal(TphPrefix), 'askhere')).
			redirects(Commands.askhere.base))

class Commands(PermCommandSet):
	Prefix = Prefix
	HelpMessage = 'TP manager help message'

	def __init__(self, *args, config, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = config
		self.__tpask_map = {}
		self.__tpsender_map = {}

	@property
	def config(self):
		return self.__config

	def has_permission(self, src: MCDR.CommandSource, literal: str) -> bool:
		return self.config.has_permission(src, literal)

	def help(self, source: MCDR.CommandSource):
		send_message(source, BIG_BLOCK_BEFOR, tr('help_msg', Prefix), BIG_BLOCK_AFTER, sep='\n')

	@Literal('pos', player_only=True)
	def tppos(self, source: MCDR.PlayerCommandSource, x: float, y: Float[-10, 300], z: float):
		server = source.get_server()
		player = source.player
		cfg = get_config()
		cmd = cfg.teleport_xyz_command.format(name=player, x=x, y=y, z=z)
		server.execute(cmd)

	@Literal('ask', player_only=True)
	def ask(self, source: MCDR.PlayerCommandSource, target: str):
		server = source.get_server()
		name = source.player
		cfg = get_config()
		# TODO: check the target player exists
		if not self.register_accept(source, target,
			lambda: [server.execute(c.format(src=name, dst=target)) for c in cfg.teleport_commands],
			lambda: send_message(source, MSG_ID, MCDR.RText(tr('ask.aborted'), color=MCDR.RColor.red)),
			lambda: send_message(source, MSG_ID, MCDR.RText(tr('ask.timeout'), color=MCDR.RColor.red)),
			timeout=cfg.teleport_expiration):
			return
		send_message(source, MSG_ID, tr('ask.sending', target),
			new_command('{} cancel'.format(Prefix), '[{}]'.format(tr('word.cancel')), color=MCDR.RColor.yellow))
		server.tell(target, join_rtext(MSG_ID, tr('ask.request_to', name),
			new_command('{} accept'.format(Prefix), '[{}]'.format(tr('word.accept')), color=MCDR.RColor.light_purple),
			new_command('{} reject'.format(Prefix), '[{}]'.format(tr('word.reject')), color=MCDR.RColor.red),
		))

	@Literal('askhere', player_only=True)
	def askhere(self, source: MCDR.PlayerCommandSource, target: str):
		server = source.get_server()
		name = source.player
		cfg = get_config()
		# TODO: check the target player exists
		if not self.register_accept(source, target,
			lambda: [server.execute(c.format(src=target, dst=name)) for c in cfg.teleport_commands],
			lambda: send_message(source, MSG_ID, MCDR.RText(tr('ask.aborted'), color=MCDR.RColor.red)),
			lambda: send_message(source, MSG_ID, MCDR.RText(tr('ask.timeout'), color=MCDR.RColor.red)),
			timeout=cfg.teleport_expiration):
			return
		send_message(source, MSG_ID, tr('ask.sending', target),
			new_command('{} cancel'.format(Prefix), '[{}]'.format(tr('word.cancel')), color=MCDR.RColor.yellow))
		server.tell(target, join_rtext(MSG_ID, tr('ask.request_from', name),
			new_command('{} accept'.format(Prefix), '[{}]'.format(tr('word.accept')), color=MCDR.RColor.light_purple),
			new_command('{} reject'.format(Prefix), '[{}]'.format(tr('word.reject')), color=MCDR.RColor.red),
		))

	@Literal('accept', player_only=True)
	def accept(self, source: MCDR.PlayerCommandSource):
		self.__tpask_map.pop(source.player,
			(lambda s: send_message(s, MCDR.RText(tr('word.no_action'), color=MCDR.RColor.red)), 0) )[0](source)

	@Literal('reject', player_only=True)
	def reject(self, source: MCDR.PlayerCommandSource):
		self.__tpask_map.pop(source.player,
			(0, lambda s: send_message(s, MCDR.RText(tr('word.no_action'), color=MCDR.RColor.red))) )[1](source)

	@Literal('cancel', player_only=True)
	def cancel(self, source: MCDR.PlayerCommandSource):
		self.__tpsender_map.pop(source.player,
			lambda s: send_message(s, MCDR.RText(tr('word.no_action'), color=MCDR.RColor.red)))(source)

	def register_accept(self, source: MCDR.PlayerCommandSource, target: str,
		accept_call, reject_call=lambda: 0,
		timeout_call=lambda: 0, timeout: int = None):
		assert isinstance(source, MCDR.PlayerCommandSource)
		assert callable(accept_call)
		assert callable(reject_call)
		assert callable(timeout_call)
		if target in self.__tpask_map:
			send_message(source, MSG_ID, MCDR.RText(tr('ask.player_req_exists', target), color=MCDR.RColor.red))
			return False
		name = source.player
		if name in self.__tpsender_map:
			send_message(source, MSG_ID, MCDR.RText(tr('ask.req_exists'), color=MCDR.RColor.red))
			return False

		tmc = (lambda: 0) if timeout is None else new_timer(timeout,
			lambda: (self.__tpask_map.pop(target), self.__tpsender_map.pop(name), timeout_call())
		).cancel
		canceler = lambda: (tmc(), self.__tpsender_map.pop(name))
		self.__tpask_map[target] = (
			lambda *args: (canceler(), dyn_call(accept_call, *args)),
			lambda *args: (canceler(), dyn_call(reject_call, *args)))
		self.__tpsender_map[name] = lambda *args: (tmc(), self.__tpask_map.pop(target), dyn_call(reject_call, *args))
		return True
