from templates import BaseDeployment
from commands.python.django.uwsgi import restart as restart_uwsgi
from fabric.context_managers import cd
from fabric.operations import run

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