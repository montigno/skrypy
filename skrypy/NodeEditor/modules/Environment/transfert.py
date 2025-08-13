class scp_transfert():
    """
    Allows to copy data between computers in a network. Needs ssh pass

    Args:
        type: (str) type of data, 'file' or 'directory'
        host_name: (string) address of the host (user@host_name)
        host_password: (string) the host password
        source: (path) path of the source
        dest: (path) path of the destination

    Returns:
        stdout: (str)

    Note:
        GUI: yes
    """
    def __init__(self, data_type="enumerate(('file', 'directory'))", direction="enumerate(('local_to_host', 'host_to_local'))",
                 host_name='', host_password='', host_path='path', local_path='path'):
        from subprocess import Popen, PIPE
        import os

        if not host_password or host_password == 'None':
            print("connection abandoned")
            self.out_pt, self.output = 'path', ''
        else:
            if direction == 'host_to_local':
                if isinstance(host_path, list):
                    host_path = ' '.join(host_path)
                    # host_path = ','.join(host_path)
                    # host_path = '"\\"{' + host_path + '"\\"}'
                source = "{}:{}".format(host_name, host_path)
                dest = local_path
                self.out_pt = os.path.join(local_path, os.path.basename(host_path))
            else:
                if isinstance(local_path, list):
                    local_path = ' '.join(local_path)
                    # local_path = ','.join(local_path)
                    # local_path = '"\\{"' + local_path + '"\\}"'
                source = local_path
                dest = "{}:{}".format(host_name, host_path)
                self.out_pt = os.path.join(host_path, os.path.basename(local_path))
            p1 = Popen(['echo', host_password], stdout=PIPE, stderr=PIPE)
            if data_type == 'directory':
                cmd = ['sshpass', '-p', host_password, 'scp', '-r', source, dest]
            else:
                cmd = ['sshpass', '-p', host_password, 'scp', source, dest]
            print(" ".join(cmd[3:]))
            p2 = Popen(cmd, stdin=p1.stdout, stdout=PIPE, stderr=PIPE)
            self.output = p2.stdout.read().decode()
            p2.communicate()
            p2.wait()
            if p2.returncode == 0:
                print('transfert done')
            else:
                print('transfert error !!, code ' + str(p2.returncode))

    def out_path(self: 'path'):
        return self.out_pt

    def stdout(self: 'str'):
        return self.output

##############################################################################


class scp_transfert_multifiles():
    """
    Allows to copy data between computers in a network. Needs ssh pass

    Args:
        type: (str) type of data, 'file' or 'directory'
        host_name: (string) address of the host (user@host_name)
        host_password: (string) the host password
        source: (path) path of the source
        dest: (path) path of the destination

    Returns:
        stdout: (str)

    Note:
        GUI: yes
    """
    def __init__(self, data_type="enumerate(('file', 'directory'))", direction="enumerate(('local_to_host', 'host_to_local'))",
                 host_name='', host_password='', host_path='path', local_path='path'):
        from subprocess import Popen, PIPE
        import os

        if not host_password or host_password == 'None':
            print("connection abandoned")
            self.out_pt, self.output = 'path', ''
        else:
            self.out_pt = []
            if direction == 'host_to_local':
                dest = local_path
                if isinstance(host_path, list):
                    source = []
                    for src in host_path:
                        source.append("{}:{}".format(host_name, src))
                        self.out_pt.append(os.path.join(local_path, os.path.basename(src))) 
                else:
                    source = ["{}:{}".format(host_name, host_path)]
                    self.out_pt = os.path.join(local_path, os.path.basename(host_path))
            else:
                dest = "{}:{}".format(host_name, host_path)
                if isinstance(local_path, list):
                    source = local_path
                    for src in source:
                        self.out_pt.append(os.path.join(host_path, os.path.basename(src))) 
                else:
                    source = [local_path]
                    self.out_pt = os.path.join(host_path, os.path.basename(local_path))
            p1 = Popen(['echo', host_password], stdout=PIPE, stderr=PIPE)
            for src in source:
                if data_type == 'directory':
                    cmd = ['sshpass', '-p', host_password, 'scp', '-r', src, dest]
                else:
                    cmd = ['sshpass', '-p', host_password, 'scp', src, dest]
                print(" ".join(cmd[3:]))
                p2 = Popen(cmd, stdin=p1.stdout, stdout=PIPE, stderr=PIPE)
                self.output = p2.stdout.read().decode()
                p2.communicate()
                p2.wait()
                if p2.returncode == 0:
                    print('transfert done')
                else:
                    print('transfert error !!, code ' + str(p2.returncode))

    def out_path(self: 'path'):
        return self.out_pt

    def stdout(self: 'str'):
        return self.output

##############################################################################


class rsync_network():
    def __init__(self, direction="enumerate(('local_to_host', 'host_to_local'))",
                 host_name='', host_password='', host_path='path', local_path='path'):
        from subprocess import Popen, PIPE

        if not host_password or host_password == 'None':
            print("connection abandoned")
            self.out_pt, self.output = 'path', ''
        else:
            if direction == 'host_to_local':
                source = "{}:{}".format(host_name, host_path)
                dest = local_path
            else:
                source = local_path
                dest = "{}:{}".format(host_name, host_path)
            p1 = Popen(['echo', host_password], stdout=PIPE, stderr=PIPE)
            cmd = ['sshpass', '-p', host_password, 'rsync', '-va', source, dest]
            print(" ".join(cmd[3:]))
            p2 = Popen(cmd, stdin=p1.stdout, stdout=PIPE)
            self.output = p2.stdout.read().decode()
            p2.communicate()
            p2.wait()
            print('synchronization done')

    def stdout(self: 'str'):
        return self.output

##############################################################################


class rsync_local():
    def __init__(self, source='path', dest='path'):
        from subprocess import Popen, PIPE

        cmd = ['rsync', '-av', source, dest]
        print(" ".join(cmd))
        p2 = Popen(cmd, stdin=PIPE, stdout=PIPE)
        self.output = p2.stdout.read().decode()
        p2.communicate()
        p2.wait()
        print('synchronization done')

    def stdout(self: 'str'):
        return self.output
