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


def rsync(local_dir, remote_dir, options={}):
    options.update({'-aurz': True})

    options["-e"] = "ssh"
    if hasattr(env, 'key_filename'):
        options["-e"] = 'ssh -p %s -i %s' % (
            env.port,
            env.key_filename
        )

    rsync_options = []
    for switch, value in options.items():
        if value == True:
            rsync_options.append(switch)
        else:
            rsync_options.append('%s "%s"' % (switch, value))
    return local("rsync %s %s %s" % (
        ' '.join(rsync_options),
        local_dir,
        remote_dir)
    )
