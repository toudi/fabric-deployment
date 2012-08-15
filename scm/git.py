# -*- coding: utf-8 *-*
from fabric.operations import local
from fabric.context_managers import lcd
from os.path import exists


class Backend:
    def __init__(self, deploy, url, config={}):
        self.deploy = deploy
        self.url = url
        self.config = config
        self.deploy.add_signal_handler('finish', self.cleanup)
        self.branch = self.deploy.branch or 'master'

    def refresh_repo(self):
        if not exists('repo'):
            local('git clone %s repo' % self.url)
        else:
            with lcd('repo'):
                local('git pull')

    """
    This method should return a tuple:
    (payload.tar.gz, files to remove)
    """
    def prepare_payload(self):
        pass


    def cleanup(self):
        local("rm -f payload.tar.gz files-to-remove")
