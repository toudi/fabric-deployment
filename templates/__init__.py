from fabric.context_managers import cd
from fabric.contrib.files import exists
from fabric.operations import run, local
from fabric.api import env
import logging
import os
from stat import S_IRGRP, S_IMODE
from commands import scp
import sys



class BaseDeployment(object):
    def __init__(self, branch=None, fast=False, fake=False, *args, **kwargs):
        self.role = env.roles[0]
        for k, v in self.get_config_value('fabric').items():
            if k == 'key_filename':
                if not self.get_config_value('fabric/forward_agent', False):
                    if v.startswith('.'):
                        foo = __import__(self.__module__)
                        v = "%s/%s" % (os.path.dirname(foo.__file__), v)
                    #Need to check if file permissions of identity file
                    #are 0600 - if not, ssh / scp will fail.
                    mod = os.stat(v).st_mode
                    if S_IMODE(mod) & S_IRGRP:
                        logging.warn("Your identity file is too open. chmod'ing it to 0600.")
                        os.chmod(v, 0600)
                else:
                    continue
                
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
        self.scm.synchronize()
        self.emit_signal("finish")

    def get_config_value(self, value, default=None, local=True):
        key_tree = value.split('/')
        tmp_val = self.config
        for key in key_tree:
            try:
                tmp_val = tmp_val[key]
            except KeyError:
                return default
        if local and type(tmp_val) == dict and (self.role or 'default' in tmp_val):
            try:
                return tmp_val[self.role]
            except KeyError:
                return tmp_val.get('default', tmp_val)
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
        tmpl = self.get_config_value('project/destpath')
        try:
            return tmpl % {
                'host': self.host()
            }
        except TypeError:
            # the host doesn't have branch placeholder
            return tmpl

    def host(self):
        return self.get_config_value('project/host')
    
    @property
    def hosts(self):
        return [self.host()]
    
    def synchronize(self, payload, delete):
        if payload:
            self.payload = payload
            self.delete = delete

            self.emit_signal("send-payload")
            self.__send_payload()
            self.emit_signal("pre-extract")
            self.__extract_payload()
            self.emit_signal("post-extract")

    def __send_payload(self):
        """Fallback method for synchronization."""
        scp(self.payload, "/tmp")
        if self.delete:
            scp(self.delete, "/tmp")
        
    def __extract_payload(self):
        #First, check if the dest.path exists.
        if not exists(self.project_path):
            run("mkdir -p %s" % self.project_path)
        #proceed to extracting the payload.
        run("tar -xzmf /tmp/%(payload)s -C %(project)s && rm -f /tmp/%(payload)s" % {
            "payload": self.payload,
            "project": self.project_path
        })

        if self.delete:
            with cd(self.project_path):
                run("rm -f `cat /tmp/%(del)s` && rm -f /tmp/%(del)s" % {'del': self.delete})
        #done deal!
