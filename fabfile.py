from fabric.api import env
import logging
import sys
from os import getcwd
from os.path import realpath, dirname


#fabfile.pyc is created in this directory even if we symlink the py file
#therefore we need to specifile fabfile.py manually
modname = __file__
if modname.endswith('pyc'):
    modname = modname[:-1]

sys.path.insert(1, dirname(realpath(modname)))


def run(command, *args, **kwargs):
    try:
        command = command.split('.')
        (module, method) = ('.'.join(command[:-1]), command[-1])
        print('commands.' + module)
        imp_cmd = __import__('commands.' + module, fromlist=[method])
        getattr(imp_cmd, method)(*args, **kwargs)
    except ImportError:
        from traceback import print_exc
        print_exc()
        logging.error("Fatal error: this command doesn't exist.")


def bootstrap(force=False):
    from config import deployment
    deploy = deployment()
    deploy.bootstrap(force)


def fastdeploy(branch=None, fake=False):
    return deploy(branch, fast=True)


def deploy(branch=None, fast=False, fake=False,*args, **kwargs):
    try:
        from config import deployment
        deploy = deployment(branch=branch, fast=fast, fake=fake, *args, **kwargs)
        deploy.run()
    except ImportError:
        from traceback import print_exc
        print_exc()
        logging.error("Deployment: you're doing it wrong. Where is the config?")
        logging.error("Hint: cd to a project dir with the config.py file")


if __name__ == 'fabfile':
    try:
        from aliases import *
    except ImportError:
        pass

    """
    Kind of a hack. deployment initializes fabric's env. Without this,
    fabric wouldn't be informed about any roledefs (this section is parsed
    before execution of functions)
    """
    try:
        from config import deployment
        deployment()
    except ImportError:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        from traceback import print_tb, print_stack, print_exc
        print_tb(exc_traceback)
        print_stack()
        print_exc()
        logging.error("Couldn't import deployment class from config module")
        logging.error("Are you in the projects dir? Apparently not!")
        logging.error(getcwd())
