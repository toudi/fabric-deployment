# -*- coding: utf-8 *-*
from templates import BaseDeployment
from commands.python import remove_pyc_files
from commands.python.django.uwsgi import restart as restart_uwsgi

class DjangoUWSGIDeployment(BaseDeployment):
    def init(self):
        self.add_signal_handler("post-extract", self.__post_extract_handler)

    def __post_extract_handler(self):
        #remove *.pyc files.
        remove_pyc_files(self.project_path)
        #restart uwsgi service.
        restart_uwsgi(self)