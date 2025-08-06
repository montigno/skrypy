class ssh_diagram_execution():
    def __init__(self, diagram=['path'], host_skrypy_path='path', host_name='', host_password='', **options):
        from subprocess import call
        import os

        if not host_password or host_password == 'None':
            print("connection abandoned")
            self.output = ''
        else:
            if not isinstance(diagram, list):
                diagram = [diagram]
            path_ssh_cmd_file = os.path.join(os.path.expanduser('~'), '.skrypy', 'ssh_command.sh')
            diagram = str(diagram).replace(' ', '')
            n_cpu = 1
            pre_exec, opx = '', ''
            if 'cpu_number' in options:
                n_cpu = options['cpu_number']
            if 'pre_exec' in options:
                pre_exec = options['pre_exec']
            if 'X11_forwarding' in options:
                if options['X11_forwarding']:
                    opx = '-X'
            with open(path_ssh_cmd_file, 'w') as fssh:
                fssh.write(pre_exec+"\n")
                fssh.write("cd {}\n".format(host_skrypy_path))
                fssh.write("source bin/activate\n")
                fssh.write("cd skrypy\n")
                fssh.write("python3 Execution_ssh.py {} {}\n".format(diagram, n_cpu))
                fssh.write("deactivate\n")
                fssh.write("echo\n")
                fssh.write("echo \"Finished.. you can close this window\"\n")
                fssh.write("echo \n")
                fssh.write("exit\n")
            os.system(f"gnome-terminal -e 'bash -c \"sshpass -p " + host_password.strip() + " ssh " + opx +
                      " " + host_name + " < ~/.skrypy/ssh_command.sh; bash\"'")

    def stdout(self: 'str'):
        return self.output

######################################################################################################################


class ssh_file_dir_exists():
    def __init__(self, path='path', host_name='', host_password=''):
        from subprocess import Popen, PIPE

        stdout, stderr = Popen(['sshpass', '-p', host_password, 'ssh', host_name,
                                'test -e ' + path + '; echo $?'], stdout=PIPE).communicate()
        self.answ = not bool(int(stdout[:-1]))

    def exists(self: 'bool'):
        return self.answ

######################################################################################################################


class ssh_list_files_in_directory():
    def __init__(self, dir='path', host_name='', host_password=''):
        from subprocess import Popen, PIPE

        stdout, stderr = Popen(['sshpass', '-p', host_password, 'ssh', host_name,
                                'ls -l ' + dir], stdout=PIPE).communicate()
        self.answ = stdout.decode()

    def exists(self: 'str'):
        return self.answ
