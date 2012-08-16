# -*- coding: utf-8 *-*
from fabric.operations import local, run
from fabric.context_managers import lcd, settings
from os.path import exists
from hashlib import md5


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
        #We need to ensure, that fabric won't exit if the .last-deployment
        #file is not on the server. This basically means, that there was no
        #deploy yet and we need to make a fresh one.
        self.removed_files_list = None
        with lcd("repo"):
            head = local("git checkout %(branch)s && git rev-parse HEAD" % {
                'branch': self.branch,
            }, capture=True)
            self.payload_file = 'payload-%s.tar.gz' % head
        with settings(warn_only=True):
            sha1 = run("cat %(project)s/.last-deployment" % {
                'project': self.deploy.project_path
            })
            if sha1.failed:
                #there was no last deployment info -> we need to deploy a full
                #tree of the code.
                with lcd("repo"):
                    local("git checkout %(branch)s && git ls-files > ../payload" % {
                        'branch': self.branch
                    })
                    local("tar -cf ../%(payload)s -T ../payload" % {
                        'payload': self.payload_file
                    })

        return (self.payload_file, self.removed_files_list)

    def cleanup(self):
        local("rm -f %(payload)s %(remove)s" % (
            self.payload_file, self.removed_files_list)
        )
