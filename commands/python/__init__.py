from fabric.operations import run, sudo
from fabric.context_managers import cd


def virtualenv(ve_path, command, use_sudo=False, cd_path=None):
    def do_virtualenv(ve_path, command, use_sudo=False):
        command = '. %(path)s/bin/activate && %(command)s' % {
            'path': ve_path,
            'command': command
        }

        if use_sudo:
            sudo(command, shell=False)
        else:
            run(command)

    if cd_path:
        with cd(cd_path):
            do_virtualenv(ve_path, command, use_sudo)
    else:
        do_virtualenv(ve_path, command, use_sudo)

def remove_pyc_files(path):
    with cd(path):
        run("find . -name '*.pyc' -delete")
