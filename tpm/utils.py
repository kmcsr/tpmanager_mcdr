
import mcdreforged.api.all as MCDR

import kpi.utils

__all__ = [
	'new_thread', 'tr'
]

kpi.utils.export_pkg(globals(), kpi.utils)

def new_thread(call):
	return MCDR.new_thread('tp_manager')(call)

def tr(key: str, *args, **kwargs):
	return MCDR.ServerInterface.get_instance().rtr(f'tpm.{key}', *args, **kwargs)
