from fabric.context_managers import cd
from fabric.contrib.files import exists
from fabric.operations import run
from fabric.api import env
import logging
import os
from stat import S_IRGRP, S_IMODE
from commands import scp



class BaseDeployment(object):
    def __init__(self, branch=None, fast=False, fake=False, *args, **kwargs):
        self.role = env.roles[0]
        for k, v in self.get_config_value('fabric').items():
            if k == 'key_filename':
                #Need to check if file permissions of identity file
                #are 0600 - if not, ssh / scp will fail.
                mod = os.stat(v).st_mode
                if S_IMODE(mod) & S_IRGRP:
                    logging.warn("Your identity file is too open. chmod'ing it to 0600.")
                    os.chmod(v, 0600)
                
            setattr(env, k, v)
        self.branch = branch
        self.fast = fast
        self.fake = fake
        self.__scm = None
        self.__signal_handlers = {}
        self.params = {
            "args": args,
            "kwargs": kwargs
        }
        self.init()

    def init(self):
        pass

    def bootstrap(self, force=False):
        pass


    def run(self):
        self.scm.refresh_repo()
        (self.payload, self.delete) = self.scm.prepare_payload()
        if self.payload:
            self.emit_signal("send-payload")
            self.__send_payload()
            self.emit_signal("pre-extract")
            self.__extract_payload()
            self.emit_signal("post-extract")
        self.emit_signal("finish")

    def get_config_value(self, value, default=None, local=True):
        key_tree = value.split('/')
        tmp_val = self.config
        for key in key_tree:
            try:
                tmp_val = tmp_val[key]
            except KeyError:
                return default
        if local and type(tmp_val) == dict and self.role in tmp_val:
            return tmp_val[self.role]
        return tmp_val

    def add_signal_handler(self, signal, handler):
        try:
            self.__signal_handlers[signal].append(handler)
        except KeyError:
            self.__signal_handlers[signal] = [handler]

    def emit_signal(self, signal, *args, **kwargs):
        for handler in self.__signal_handlers.get(signal, []):
            handler(*args, **kwargs)

    @property
    def scm(self):
        if not self.__scm:
            scm_class = 'scm.' + self.get_config_value('scm/class')
            scm_url = self.get_config_value('scm/url')
            scm_config = self.get_config_value('scm/config', default={})
            _imp = __import__(scm_class, fromlist=['Backend'])
            self.__scm = getattr(_imp, 'Backend')(self, scm_url, scm_config)
        return self.__scm

    @property
    def project_path(self):
        return self.get_config_value('project/destpath') % {
            'host': self.host()
        }

    def host(self):
        return self.get_config_value('project/host')
    
    @property
    def hosts(self):
        return [self.host()]
    
    def __send_payload(self):
        scp(self.payload, "/tmp")
        if self.delete:
            scp(self.delete, "/tmp")
        
    def __extract_payload(self):
        #First, check if the dest.path exists.
        if not exists(self.project_path):
            run("mkdir -p %s" % self.project_path)
        #proceed to extracting the payload.
        run("tar -xzmf /tmp/%(payload)s -C %(project)s" % {
            "payload": self.payload,
            "project": self.project_path
        })
        if self.delete:
            with cd(self.project_path):
                run("rm -f `cat /tmp/%s`" % self.delete)
        #done deal!
