class path_SharedMemory_create():
    def __init__(self, memoryName='', path='path', **options):
        from multiprocessing import shared_memory
        memoryName = memoryName.strip()
        path = path.strip()
        length_path = len(path)
        print(memoryName, path, length_path)
        self.path = 'path'
        if 'overwrite' in options:
            if options['overwrite']:
                try:
                    shared_data = shared_memory.SharedMemory(memoryName, create=True, size=length_path)
                except Exception as err:
                    shared_data = shared_memory.SharedMemory(memoryName)
                    shared_data.close()
                    shared_data.unlink()
                    shared_data = shared_memory.SharedMemory(memoryName, create=True, size=length_path)
            else:
                shared_data = shared_memory.SharedMemory(memoryName, create=True, size=length_path)
        else:
            try:
                shared_data = shared_memory.SharedMemory(memoryName, create=True, size=length_path)
            except Exception as err:
                self.path = 'no path'
        buffer = shared_data.buf
        buffer[:length_path] = bytes(path, encoding='utf-8')
        shared_data.close()
        if self.path != 'no path':
            self.path = path

    def out_path(self: 'path'):
        return self.path

##############################################################################


class path_SharedMemory_read():
    def __init__(self, memoryName='', **options):
        from multiprocessing import shared_memory
        # import array
        memoryName = memoryName.strip()
        self.existing_shm = ''
        try:
            shm = shared_memory.SharedMemory(memoryName)
            self.existing_shm = bytes(shm.buf[:shm.size]).decode()
            shm.close()
            if 'cleanup' in options:
                if options['cleanup']:
                    shm.unlink()
        except Exception as err:
            print(err)

    def out_path(self: 'path'):
        return self.existing_shm

##############################################################################


class list_SharedMemory():
    def __init__(self):
        import os
        list_path = os.path.join(os.path.expanduser("~"), '.skrypy', 'list_shm.tmp')
        self.l_shm = []
        if os.path.exists(list_path):
            f = open(list_path)
            content = f.read()
            f.close()
            content = content.replace('{', '')
            content = content.replace('}', '')
            content = content.replace("'", '')
            self.l_shm = content.split(',')

    def list_shm(self: 'list_str'):
        return self.l_shm

##############################################################################


class clean_RAM():
    def __init__(self, sudo_password=''):
        # from NodeEditor.modules.Environment.authentification import passwd_dialog
        from subprocess import Popen, PIPE

        # sudo_password = passwd_dialog("Enter your sudo password").passwd()
        if not sudo_password or sudo_password == 'None':
            print("RAM cleaning abandoned")
            self.output = ''
        else:
            p1 = Popen(['echo', sudo_password], stdout=PIPE, stderr=PIPE)
            p2 = Popen(['sudo', '-S', 'sysctl', 'vm.drop_caches=3'], stdin=p1.stdout, stdout=PIPE)
            self.output = p2.stdout.read().decode()
            p2.communicate()
            print('RAM cleaning done')

    def stdout(self: 'str'):
        return self.output

##############################################################################


class clean_SWAP():
    def __init__(self, sudo_password=''):
        # from NodeEditor.modules.Environment.authentification import passwd_dialog
        from subprocess import Popen, PIPE

        # sudo_password = passwd_dialog("Enter your sudo password").passwd()
        if not sudo_password or sudo_password == 'None':
            print("SWAP cleaning abandoned")
            self.output = ''
        else:
            p1 = Popen(['echo', sudo_password], stdout=PIPE)
            p2 = Popen(['sudo', '-S', 'swapoff', '-a'], stdin=p1.stdout, stdout=PIPE)
            p2.communicate()
            p3 = Popen(['echo', sudo_password], stdout=PIPE)
            p4 = Popen(['sudo', '-S', 'swapon', '-a'], stdin=p3.stdout, stdout=PIPE)
            self.output = p4.stdout.read().decode()
            p4.communicate()
            print('SWAP cleaning done')

    def stdout(self: 'str'):
        return self.output
