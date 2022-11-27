
import mcdreforged.api.all as MCDR

from .globals import *
from .utils import *
from .api import *

Prefix = '!!tp'
TpaPrefix = '!!tpa'
TphPrefix = '!!tph'

def register(server: MCDR.PluginServerInterface):
	cfg = get_config()
	server.register_help_message(Prefix, 'TP manager help message')
	server.register_help_message(TpaPrefix, 'Teleport to somebody')
	server.register_help_message(TphPrefix, 'Teleport somebody here')

	tpa_node = (cfg.literal('ask').
		requires(lambda src: src.is_player, lambda: MCDR.RText('Only player can use this command', color=MCDR.RColor.red)).
		then(MCDR.Text('name').runs(lambda src, ctx: command_ask(src, ctx['name'])))
	)
	tph_node = (cfg.literal('askhere').
		requires(lambda src: src.is_player, lambda: MCDR.RText('Only player can use this command', color=MCDR.RColor.red)).
		then(MCDR.Text('name').runs(lambda src, ctx: command_askhere(src, ctx['name'])))
	)

	server.register_command(
		MCDR.Literal(Prefix).
		runs(command_help).
		then(cfg.literal('help').runs(command_help)).
		then(cfg.literal('pos').
			requires(lambda src: src.is_player, lambda: MCDR.RText('Only player can use this command', color=MCDR.RColor.red)).
			then(MCDR.Float('x').then(MCDR.Float('y').then(MCDR.Float('z').
			runs(lambda src, ctx: command_tppos(src, src.player, ctx['x'], ctx['y'], ctx['z'])))))).
		then(tpa_node).
		then(tph_node).
		then(cfg.literal('accept').
			requires(lambda src: src.is_player, lambda: MCDR.RText('Only player can use this command', color=MCDR.RColor.red)).
			runs(command_accept)).
		then(cfg.literal('reject').
			requires(lambda src: src.is_player, lambda: MCDR.RText('Only player can use this command', color=MCDR.RColor.red)).
			runs(command_reject))
	)
	server.register_command(MCDR.Literal(TpaPrefix).redirects(tpa_node))
	server.register_command(MCDR.Literal(TphPrefix).redirects(tph_node))

def command_help(source: MCDR.CommandSource):
	send_message(source, BIG_BLOCK_BEFOR, tr('help_msg', Prefix), BIG_BLOCK_AFTER, sep='\n')

def command_tppos(source: MCDR.CommandSource, player: str, x: float, y: float, z: float):
	server = source.get_server()
	cfg = get_config()
	cmd = cfg.teleport_xyz_command.format(name=player, x=x, y=y, z=z)
	server.execute(cmd)

def command_ask(source: MCDR.CommandSource, target: str):
	server = source.get_server()
	name = source.player
	cfg = get_config()
	# TODO: check the target player exists
	if not register_accept(target,
		lambda: [server.execute(c.format(src=name, dst=target)) for c in cfg.teleport_commands],
		lambda: send_message(source, MSG_ID, MCDR.RText(tr('ask.aborted'), color=MCDR.RColor.red)),
		timeout=cfg.teleport_expiration):
		send_message(source, MSG_ID, MCDR.RText(tr('ask.already_have_req'), color=MCDR.RColor.red))
		return
	send_message(source, MSG_ID, tr('ask.sending'))
	server.tell(target, join_rtext(MSG_ID, tr('ask.request_to', name),
		new_command('{} accept'.format(Prefix), '[{}]'.format(tr('word.accept')), color=MCDR.RColor.light_purple),
		new_command('{} reject'.format(Prefix), '[{}]'.format(tr('word.reject')), color=MCDR.RColor.red),
	))

def command_askhere(source: MCDR.CommandSource, target: str):
	server = source.get_server()
	name = source.player
	cfg = get_config()
	# TODO: check the target player exists
	if not register_accept(target,
		lambda: [server.execute(c.format(src=target, dst=name)) for c in cfg.teleport_commands],
		lambda: send_message(source, MSG_ID, MCDR.RText(tr('ask.aborted'), color=MCDR.RColor.red)),
		timeout=cfg.teleport_expiration):
		send_message(source, MSG_ID, MCDR.RText(tr('ask.already_have_req'), color=MCDR.RColor.red))
		return
	send_message(source, MSG_ID, tr('ask.sending'))
	server.tell(target, join_rtext(MSG_ID, tr('ask.request_from', name),
		new_command('{} accept'.format(Prefix), '[{}]'.format(tr('word.accept')), color=MCDR.RColor.light_purple),
		new_command('{} reject'.format(Prefix), '[{}]'.format(tr('word.reject')), color=MCDR.RColor.red),
	))

def command_accept(source: MCDR.CommandSource):
	tpask_map.pop(source.player, (lambda s: send_message(s, MCDR.RText(tr('word.no_action'), color=MCDR.RColor.red), 0)))[0](source)

def command_reject(source: MCDR.CommandSource):
	tpask_map.pop(source.player, (0, lambda s: send_message(s, MCDR.RText(tr('word.no_action'), color=MCDR.RColor.red))))[1](source)

tpask_map = {}

def __warp_call(call, c=None):
	def w(*b):
		if c is not None:
			c()
		return call(*b[:call.__code__.co_argcount])
	return w

def register_accept(player: str, accept_call, reject_call=lambda: 0, timeout_call=lambda: 0, timeout: int = None, *, cover: bool = False):
	if not cover and player in tpask_map:
		return False
	tmc = None if timeout is None else new_timer(timeout, lambda: (
		tpask_map.pop(player),
		timeout_call()
	)).cancel
	tpask_map[player] = (__warp_call(accept_call, tmc), __warp_call(reject_call, tmc))
	return True
