class ssh_file_dir_exists():
    """
    docstring to be completed
    """
    def __init__(self,
                 path='path',
                 host_name='',
                 host_password=''):

        from subprocess import Popen, PIPE

        stdout, _ = Popen(['sshpass', '-p', host_password, 'ssh', host_name,
                           'test -e ' + path + '; echo $?'], stdout=PIPE).communicate()
        self.answ = not bool(int(stdout[:-1]))

    def exists(self) -> bool:
        return self.answ

######################################################################################################################


class ssh_list_files_in_directory():
    """
    docstring to be completed
    """
    def __init__(self,
                 dirt='path',
                 host_name='',
                 host_password=''):

        from subprocess import Popen, PIPE

        stdout, _ = Popen(['sshpass', '-p', host_password, 'ssh', host_name,
                           'ls -l ' + dirt], stdout=PIPE).communicate()
        self.answ = stdout.decode()

    def exists(self) -> str:
        return self.answ

######################################################################################################################


class ssh_get_size():
    """
    docstring to be completed
    """
    def __init__(self,
                 dir_or_file='path',
                 host_name='',
                 host_password=''):

        from subprocess import Popen, PIPE

        stdout, _ = Popen(['sshpass', '-p', host_password, 'ssh', host_name,
                           'du -msh ' + dir_or_file], stdout=PIPE).communicate()
        self.answ = stdout.decode()

    def size(self) -> str:
        return self.answ

######################################################################################################################
