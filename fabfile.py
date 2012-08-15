import logging
import sys
from os import getcwd
for path in ('', '../../'):
    if not getcwd() + '/' + path in sys.path:
        sys.path.insert(1, getcwd() + '/' + path)

try:
    from aliases import *
except ImportError:
    pass

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


def fastdeploy(branch=None):
    return deploy(branch, fast=True)


def deploy(branch=None, fast=False):
    try:
        from config import deployment
        deploy = deployment(branch=branch, fast=fast)
        deploy.run()
    except ImportError:
        from traceback import print_exc
        print_exc()
        logging.error("Deployment: you're doing it wrong. Where is the config?")
        logging.error("Hint: cd to a project dir with the config.py file")


if __name__ == 'fabfile':
    """
    Kind of a hack. deployment initializes fabric's env. Without this,
    fabric wouldn't be informed about any roledefs (this section is parsed
    before execution of functions)
    """
    from config import deployment
    deploy = deployment()