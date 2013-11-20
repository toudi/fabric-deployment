from fabric.operations import run, sudo


def SUPERVISORCTL_COMMAND(cmd, cfg=None):
    if cfg:
        cfg = '-c '+cfg
    return "supervisorctl %(cfg)s%(command)s" % {'cfg': cfg or '', 'command': cmd}


def run_or_sudo(cmd, use_sudo):
    if use_sudo:
        sudo(cmd, shell=False)
    else:
        run(cmd)

def restart(name, cfg=None, use_sudo=False):
    run_or_sudo(SUPERVISORCTL_COMMAND("restart %s" % name, cfg), use_sudo)

def start(name, cfg=None, use_sudo=False):
    run_or_sudo(SUPERVISORCTL_COMMAND("start %s" % name, cfg), use_sudo)

def stop(name, cfg=None, use_sudo=False):
    run_or_sudo(SUPERVISORCTL_COMMAND("stop %s" % name, cfg), use_sudo)

def stop_group(group, cfg=None, use_sudo=False):
    stop("%s:*" % group, cfg, use_sudo)

def start_group(group, cfg=None, use_sudo=False):
    start("%s:*" % group, cfg, use_sudo)

def reload_cfg(cfg=None, use_sudo=False):
    run_or_sudo(SUPERVISORCTL_COMMAND("update", cfg), use_sudo)
