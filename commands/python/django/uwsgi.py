# -*- coding: utf-8 *-*
"""
These uwsgi commands are very tightly connected to django deployment
and / or virtualenv.
"""
from commands.python import virtualenv
from commands import scp
from fabric.context_managers import settings, cd
from fabric.contrib.files import exists
from fabric.operations import run
import logging

def is_running(deployment):
    if not exists("%s/uwsgi.pid" % deployment.get_config_value('uwsgi/workdir')):
        return False
    with settings(warn_only=True):
        uwsgi_running = run("kill -s 0 `cat %(uwsgi)s/uwsgi.pid`" % {
            "uwsgi": deployment.get_config_value('uwsgi/workdir')
        })
        
        return not uwsgi_running.failed

def restart(deployment):
    #we need to check whether uwsgi is started in emperor mode or not.
    emperor = deployment.get_config_value('uwsgi/emperor', True)
    vassals_dir = deployment.get_config_value('uwsgi/vassals_dir')
    #then, check if the master instance of uwsgi exists. If not, there's no
    #need to restart, as it will pick up vassal automatically.
        
    if emperor:
        with cd(vassals_dir):
            if not is_running(deployment):
                #start uwsgi, as it will pick up the vassal from vassal's dir.
                start(deployment)
                return
            if exists(deployment.vassal[0]):
                run("touch %s" % deployment.vassal[0])
            else:
                scp(
                    deployment.get_config_value('uwsgi/launcher'),
                    vassals_dir + "/" + deployment.vassal[0]
                )
    else:
        stop(deployment)
        start(deployment)

def start(deployment):
    #we need to check whether uwsgi is started in emperor mode or not.
    emperor = deployment.get_config_value('uwsgi/emperor', True)
    uwsgi_dir = deployment.get_config_value('uwsgi/workdir')
    
    vassal = deployment.vassal
    if emperor:
        #in emperor mode, we create the vassal file.
        vassals_dir = deployment.get_config_value('uwsgi/vassals_dir')
        if not exists(vassals_dir):
            run("mkdir -p %s" % vassals_dir)
        with cd(vassals_dir):
            if not exists(vassal[0]):
                if vassal[1]:
                    run("ln -s %s %s" % (vassal[1], vassal[0]))
                else:
                    scp(
                        deployment.get_config_value('uwsgi/launcher'),
                        vassals_dir + "/" + vassal[0]
                    )
        if not is_running(deployment):
        #let's start main uwsgi instance.
            virtualenv(
                deployment.get_config_value('virtualenv/path'),
                "LANG=pl_PL.UTF-8 LC_ALL=pl_PL.UTF-8 uwsgi --master \
 --emperor %(vassals)s --daemonize %(log)s --pidfile %(pid)s --fastrouter %(sock)s \
 --fastrouter-subscription-server 127.0.0.1:3032" % {
                    "log": uwsgi_dir + "/uwsgi.log",
                    "pid": uwsgi_dir + "/uwsgi.pid",
                    "vassals": vassals_dir,
                    "sock": uwsgi_dir + "/uwsgi.sock"
                }
            )


    else:
        #not emperor mode - start uwsgi process.
        virtualenv(
            deployment.get_config_value('virtualenv/path'),
            "LANG=pl_PL.UTF-8 LC_ALL=pl_PL.UTF-8 uwsgi \
 --daemonize %(log)s --pidfile %(pid)s --socket %(sock)s %(def)s" % {
                "log": project_path + "/uwsgi.log",
                "pid": project_path + "/uwsgi.pid",
                "def": vassal[1],
                "sock": project_path + "/uwsgi.sock"
            }
        )

def stop(deployment):
    #we need to check whether uwsgi is started in emperor mode or not.
    emperor = deployment.get_config_value('uwsgi/emperor', True)
    vassal = deployment.vassal
    if emperor:
        #in emperor mode, we remove the config file.
        run("rm -f %s/%s" % (
                deployment.get_config_value('uwsgi/vassals_dir'),
                vassal[0]
            )
        )
    else:
        #not emperor mode - we can simply kill the uwsgi process.
        run("kill -TERM `cat %s/uwsgi.pid`" % deployment.project_path)
        run("rm -f %s/uwsgi.pid" % deployment.project_path)