from uwsgi import UWSGIDeployment
from commands.python import virtualenv


class PylonsUwsgiDeployment(UWSGIDeployment):
    def bootstrap(self, force=False):
        super(PylonsUwsgiDeployment, self).bootstrap(force)
        #uwsgi was installed in UWSGIDeployment, so we can proceed to installing pylons
        virtualenv(
            self.get_config_value('virtualenv/path'),
            "pip install Pylons"
        )