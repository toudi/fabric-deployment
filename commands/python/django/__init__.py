# -*- coding: utf-8 *-*
import os, os.path
from fabric.operations import local, run
from fabric.context_managers import settings
from fabric.state import env
from fabric.contrib.files import exists
import logging

def bootstrap():
    #Let's check if ssh identity exists.
    ssh_ident_dir = os.getcwd() + '/../ssh-keys/'
    if not os.path.exists(ssh_ident_dir):
        os.mkdir(ssh_ident_dir)
        local('ssh-keygen -t rsa -f %s/id_rsa' % ssh_ident_dir)
        logging.warning(
            "You need to create the deployer's account on the server\n\
            and copy the id_rsa.pub file by command:\n\
            ssh-copy-id -i %s/id_rsa user@remote\n" % ssh_ident_dir
        )
        return

    uwsgi_workdir = self.getConfigValue('uwsgi/work_dir')
    if not uwsgi_workdir:
        logging.error('you need to specify uwsgi/work_dir in your config!')
        return

    print(self.getConfigValue('roledefs', local=False)[self.role])
    with settings(
        roles=[self.role], roledefs=self.getConfigValue('roledefs', local=False),
        hosts=self.hosts
    ):
        if not exists(uwsgi_workdir):
            run('mkdir %s' % uwsgi_workdir)
