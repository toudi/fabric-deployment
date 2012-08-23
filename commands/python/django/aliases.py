from config import deployment
from commands.python.django.uwsgi import start, stop, restart

def start_uwsgi(*args, **kwargs):
    return start(deployment(*args, **kwargs))

def stop_uwsgi(*args, **kwargs):
    return stop(deployment(*args, **kwargs))

def restart_uwsgi(*args, **kwargs):
    return restart(deployment(*args, **kwargs))