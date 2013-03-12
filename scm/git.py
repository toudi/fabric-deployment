# -*- coding: utf-8 *-*
from fabric.api import env
from fabric.operations import local, run
from fabric.context_managers import lcd, settings
from fabric.contrib.files import exists as rexists
from os.path import exists
from hashlib import md5
from commands import rsync


class Backend:
    def __init__(self, deploy, url, config={}):
        self.deploy = deploy
        self.url = url
        self.config = config
        self.deploy.add_signal_handler('finish', self.finish)
        self.branch = self.deploy.branch or 'master'
        _rsync = local("rsync --version > /dev/null")
        self.use_rsync = not _rsync.failed

    def refresh_repo(self):
        if not exists('repo'):
            local('git clone %s repo' % self.url)
        else:
            with lcd('repo'):
                local('git pull')

    def synchronize(self):
        self.refresh_repo()

        if not rexists(self.deploy.project_path):
            run('mkdir -p %s' % self.deploy.project_path)
        if self.use_rsync:
            self.deploy.emit_signal('send-payload')
            self.deploy.emit_signal('pre-extract')
            with lcd('repo'):
                local("git checkout %s" % self.branch)
                local("git pull")
                rsync_options = {
                    '--progress': True,
                    '--exclude': '.git*',
                }
                rsync(
                    "./",
                    "%(user)s@%(host)s:%(project)s" % {
                        "user": env.user,
                        "host": env.host,
                        "project": self.deploy.project_path
                    },
                    rsync_options
                )
                #local("git checkout master")
                #Leaving this get's rsync to re-send the files that git has created in
                #the checkout.
            self.deploy.emit_signal('post-extract')
        else:
            self.synchronize_without_rsync()
    """
    This method should return a tuple:
    (payload.tar.gz, files to remove)
    """
    def synchronize_without_rsync(self):
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
                local("git pull")
                self.head = local("git checkout %(branch)s && git rev-parse HEAD" % {
                    'branch': self.branch,
                }, capture=True)
                if not self.deploy.fake:
                    self.prepare_change_files(sha1)

                #just in case enything goes berserk in the future
                #we bail out to master branch, so future deploys
                #could resume sanely.
                local("git checkout master")

        if self.payload_file and not self.deploy.fake:
            self.deploy.synchronize(self.payload_file, self.removed_files_list)

    def finish(self):
        if not self.use_rsync:
            #do the stuff only if there was something changed.
            if self.payload_file:
                local("rm -f payload %(payload)s %(remove)s" % {
                    'payload': self.payload_file,
                    'remove': self.removed_files_list
                })
                run("rm -f /tmp/" + self.payload_file)
                
            if self.payload_file or self.deploy.fake:
                run("echo %(head)s > %(project)s/.last-deployment" % {
                    "head": self.head,
                    "project": self.deploy.project_path
                })

    def prepare_change_files(sha1):
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
                self.removed_files_list = "remove-files-%s" % self.head
            #we prepare the diff
                local("git diff --name-status --no-renames %s |\
egrep '^(A|M)' | cut -f 2 > ../payload" % sha1)
                local("git diff --name-status --no-renames %s |\
egrep '^D' | cut -f 2 > ../%s" % (sha1, self.removed_files_list))
            else:
                self.payload_file = None

        if self.payload_file:
            local("tar -czf ../%(payload)s -T ../payload" % {
                'payload': self.payload_file
            })
