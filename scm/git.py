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
        self.deploy.add_signal_handler('finish', self.finish)
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
        self.payload_file = None

        with settings(warn_only=True):
            sha1 = run("cat %(project)s/.last-deployment" % {
                'project': self.deploy.project_path
            })
            with lcd("repo"):
                local("git checkout %s" % self.branch)
                self.head = local("git checkout %(branch)s && git rev-parse HEAD" % {
                    'branch': self.branch,
                }, capture=True)
                self.payload_file = 'payload-%s.tar.gz' % self.head
                if sha1.failed:
                    #there was no last deployment info -> we need to deploy a full
                    #tree of the code.
                        local("git ls-files > ../payload" % {
                            'branch': self.branch
                        })
                        local("tar -czf ../%(payload)s -T ../payload" % {
                            'payload': self.payload_file
                        })
                else:
                    if self.head != sha1:
                    #we prepare the diff
                        local("git diff --name-status --no-renames %s |\
                                   egrep '^(A|M)' | cut -f 2 > ../payload" % sha1)
                        local("git diff --name-status --no-renames %s |\
                                   egrep '^D' | cut -f 2 > ../remove-files" % sha1)
                    else:
                        self.payload_file = None
                #just in case enything goes berserk in the future
                #we bail out to master branch, so future deploys
                #could resume sanely.
                local("git checkout master")
                
            if self.payload_file:
                local("tar -czf ../%(payload)s -T ../payload" % {
                    'payload': self.payload_file
                })

                            
        return (self.payload_file, self.removed_files_list)

    def finish(self):
        if self.payload_file:
            local("rm -f payload %(payload)s %(remove)s" % {
                'payload': self.payload_file,
                'remove': self.removed_files_list
            })
            run("rm -f /tmp/" + self.payload_file)
        run("echo %(head)s > %(project)s/.last-deployment" % {
            "head": self.head,
            "project": self.deploy.project_path
        })
