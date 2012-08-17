from templates import BaseDeployment


class PythonDeployment(BaseDeployment):
    def init(self):
        self.add_signal_handler('post-extract', self.remove_pyc_files)

    def remove_pyc_files(self):
        from commands.python import remove_pyc_files
        remove_pyc_files(self.project_path)
