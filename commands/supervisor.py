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


def stop_group(group, cfg=None, use_sudo=False):
    run_or_sudo(SUPERVISORCTL_COMMAND("stop %s:*" % group, cfg), use_sudo)


def start_group(group, cfg=None, use_sudo=False):
    run_or_sudo(SUPERVISORCTL_COMMAND("start %s:*" % group, cfg), use_sudo)


def reload_cfg(cfg=None, use_sudo=False):
    run_or_sudo(SUPERVISORCTL_COMMAND("reread", cfg), use_sudo)
