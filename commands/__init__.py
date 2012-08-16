from fabric.operations import local
from fabric.api import env

def scp(local_file, remote_file):
    return local("scp -P %(port)s -i %(ident)s %(local_file)s %(user)s@%(host)s:%(remote_file)s" % (
        {
            "port": env.port,
            "ident": env.key_filename,
            "local_file": local_file,
            "user": env.user,
            "host": env.host,
            "remote_file": remote_file
        }
    ))
