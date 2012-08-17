from config import deployment
from commands.python.django.uwsgi import start, stop, restart

def start_uwsgi():
    return start(deployment())

def stop_uwsgi():
    return stop(deployment())

def restart_uwsgi():
    return restart(deployment())