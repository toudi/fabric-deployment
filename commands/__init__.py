from fabric.operations import local
from fabric.api import env, settings, run
import os.path

CMD_AGENT   = "scp -P %(port)s %(local_file)s %(user)s@%(host)s:%(remote_file)s"
CMD_NOAGENT = "scp -P %(port)s -i %(ident)s %(local_file)s %(user)s@%(host)s:%(remote_file)s"

def scp(local_file, remote_file):
    args = {
        "port": env.port,
        "local_file": local_file,
        "user": env.user,
        "host": env.host,
        "remote_file": remote_file
    }

    if os.path.isdir(local_file):
        args['local_file'] = '-r %s' % local_file

    cmd = CMD_AGENT

    if not env.forward_agent:
        cmd = CMD_NOAGENT
        args['ident'] = env.key_filename

    return local(cmd % args)

RSYNC_SSH_NOAGENT = "ssh -p %(port)s -i %(ident)s"
RSYNC_SSH_AGENT   = "ssh -A -p %(port)s"

def rsync(local_dir, remote_dir, options={}):
    options.update({'-aurz': True})

    ssh_args = {'port': env.port}
    ssh_cmd  = RSYNC_SSH_AGENT

    if hasattr(env, 'key_filename') and not env.forward_agent:
        ssh_cmd = RSYNC_SSH_NOAGENT
        ssh_args['ident'] = env.key_filename

    options["-e"] = ssh_cmd % ssh_args

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


def is_link(path):
    with settings(warn_only=True):
        return run('[ -L "%s" ]' % path).succeeded

def sed_replace(replace_dict, path, search_wrapper='__%s__', auto_escape=True):
    """
    Executes sed in 'edit-in-place' mode, replacing all of `search`
    occurences with `replace`.
    You need to pass `replace_dict` as a dict, where keys are searches
    and values are replacements.
    
    param auto_escape - specifies whether the values should be searched for '/' and auto escaped
    This is usually a wise thing to do with sed, however if you do it yourself, then set this value
    to false.
    """
    replace_tmpl = "s/%(search)s/%(replace)s/g;"
    sed_cmd      = "sed -i -e'%s' %s"

    r = []

    for search, _replace in replace_dict.items():
        if auto_escape:
            _replace = _replace.replace('/', '\/')
        r.append(replace_tmpl % {
            'search': search_wrapper % search,
            'replace': _replace
        })

    run(sed_cmd % (''.join(r), path))
    del r
