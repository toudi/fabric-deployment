from templates import BaseDeployment
from commands.python.django.uwsgi import restart as restart_uwsgi
from commands.python import virtualenv
from fabric.context_managers import cd
from fabric.operations import run
from fabric.contrib.files import exists

class UWSGIDeployment(BaseDeployment):
    def init(self):
        self.add_signal_handler("finish", self.restart)
            
    """
    Return tuple:
     (launcher-file, template-file)
    where:
     launcher-file - filename of the launcher.
     template-file - if not None, filename of the template we should link to.
    """
    @property
    def vassal(self):
        return (
            self.host() + ".ini",
            self.get_config_value('uwsgi/vassal_template')
        )
    
    def restart(self):
        if not self.fast:
            #update the domains.
            with cd(self.project_path):
                run("echo \"%s\" > domains.txt" % "\n".join(self.hosts))
        restart_uwsgi(self)
        
    def bootstrap(self, force=False):
        vassals_dir = self.get_config_value('uwsgi/vassals_dir')
        uwsgi_dir = self.get_config_value('uwsgi/workdir')
        virtualenv_dir = self.get_config_value('virtualenv/path')
        virtualenv_bin = self.get_config_value('virtualenv/bin', 'virtualenv')

        if not exists(virtualenv_dir) or force:
            run("%s %s" % (virtualenv_bin, virtualenv_dir))
            virtualenv(virtualenv_dir, "pip install uwsgi")

        for p in (uwsgi_dir, vassals_dir):
            if not exists(p) or force:
                run('mkdir %s' % p)
        