from uwsgi import UWSGIDeployment


class PylonsUwsgiDeployment(UWSGIDeployment):
    def bootstrap(self, force=False):
        from commands.python import virtualenv

        uwsgi_dir = self.get_config_value('uwsgi/work_dir')
        virtualenv_dir = self.get_config_value('virtualenv/path')
        virtualenv_bin = self.get_config_value('virtualenv/bin')

        vassals_dir = self.get_config_value('uwsgi/vassals_dir')

        if not exists(virtualenv_dir) or force:
            run("%s %s" % (virtualenv_bin, virtualenv_dir))
            virtualenv(virtualenv_dir, "pip install uwsgi")

        for p in (uwsgi_dir, vassals_dir):
            if not exists(p) or force:
                run('mkdir %s' % p)
