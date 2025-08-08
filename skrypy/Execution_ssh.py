from PyQt5.QtCore import QRunnable

from NodeEditor.ssh.Diagram_Execution_dep import execution2

from multiprocessing import shared_memory
import os
import ast
import sys
import gc
import yaml
from PyQt5.QtWidgets import QApplication


class execution_ssh():

    def __init__(self, workspace, files_dgr, n_cpu, mode, parent=None):
        files_dgr = files_dgr[1:-1].split(',')
        self.n_cpu = int(n_cpu)
        self.loadSharedMemoryFromYaml(workspace)
        # if os.environ.get("SHME_SKRYPY") is not None:
        #     self.loadSharedMemoryFromClient()
        env_param_diagram = os.path.join(os.path.expanduser('~'), '.skrypy', 'env_parameters.dgr')
        files_dgr = [env_param_diagram] + files_dgr
        for dgr in files_dgr:
            self.execute_Diagram(dgr, mode)

    def loadSharedMemoryFromClient(self):
        print('os.environ["SHME_SKRYPY"]=', os.environ["SHME_SKRYPY"])
        shme_client = ast.literal_eval(os.environ["SHME_SKRYPY"])
        file_shm_server = os.path.join(os.path.expanduser('~'), '.skrypy', 'list_shm.tmp')
        list_name = []
        for var_name, var_value in shme_client.items():
            length_path = len(var_value)
            shared_data = shared_memory.SharedMemory(var_name.strip(), create=True, size=length_path)
            buffer = shared_data.buf
            buffer[:length_path] = bytes(var_value.strip(), encoding='utf-8')
            shared_data.close()
            list_name.append(var_name.strip())
        with open(file_shm_server, 'w') as f:
            f.write(str(list_name))
        with open(file_shm_server, 'r') as f:
            print("list_shm_file:", f.read())
            # print('shme_client:', shme_client)
            
    def loadSharedMemoryFromYaml(self, wrksp):
        yaml_file_shme = os.path.join(wrksp, 'shme_transfered.yml')
        with open(yaml_file_shme, 'r') as stream:
            outYaml = yaml.load(stream, yaml.FullLoader)
        print('outYaml', outYaml)
        file_shm_server = os.path.join(os.path.expanduser('~'), '.skrypy', 'list_shm.tmp')
        list_name = []
        for var_name, var_value in outYaml.items():
            length_path = len(var_value)
            shared_data = shared_memory.SharedMemory(var_name.strip(), create=True, size=length_path)
            buffer = shared_data.buf
            buffer[:length_path] = bytes(var_value.strip(), encoding='utf-8')
            shared_data.close()
            list_name.append(var_name.strip())
        with open(file_shm_server, 'w') as f:
            f.write(str(list_name))
        with open(file_shm_server, 'r') as f:
            print("list_shm_file:", f.read())
            # print('shme_client:', shme_client)

    def execute_Diagram(self, file_dgr, mode):
        gc.collect()
        title_dgr = os.path.basename(file_dgr)

        # with open(file_dgr) as f:
        #     txt_code = f.read()
        file_head = ''
        file_end = ''

        with open(file_dgr) as f:
            i = 0
            move = False
            for line in f:
                if '[execution]' in line:
                    move = True
                if move:
                    i += 1
                if 1 < i < 8:
                    file_head += line
                else:
                    if '[execution]' not in line:
                        file_end += line
                if i == 8:
                    move = False

        txt_code = file_head + file_end
        print('\n' * 2)
        print("execution: {}".format(title_dgr))
        # if mode_th:
        #     mode = 'Multi-threading'
        # else:
        #     mode = 'Sequential'

        if self.check_script_code(txt_code):
            editor.editText("Warning: some scripts contain the terms 'QApplication' or 'syst.exit', remove them !",
                            10, 600, 'ff0000', False, True)
            return

        print(" {} execution: ".format(mode))
        print("     > started")
        print("     > in progress ...")

        args = (txt_code, {}, '')

        # current_dir_path = os.path.dirname(os.path.realpath(__file__))
        # source_disp = os.path.join(current_dir_path, 'tasks_progress.py')
        # subprocess.Popen([sys.executable, source_disp, 'start diagram'])
        self.runner = ThreadDiagram(title_dgr, args, self.n_cpu)
        try:
            sr = self.runner.run()
        except Exception as err:
            print("\n\33[31mThis diagram contains errors : {}\33[0m".format(str(err)))
        SharedMemoryManager(False)
        # self.runner.sysctrl.kill()
        # for proc in psutil.process_iter():
        #     print("pid:", proc.name())

        # self.runner = Window_progressbar(title_dgr, args, editor)
        # self.runner.close()

    def check_script_code(self, txt):
        if 'QApplication(' in txt:
            return True
        return False


class SharedMemoryManager():

    def __init__(self, empt):
        super(SharedMemoryManager, self).__init__()
        self.file_shm = os.path.join(os.path.expanduser('~'), '.skrypy', 'list_shm.tmp')
        if empt:
            pass
        else:
            self.readList(empt)

    def readList(self, toEmpty):
        if os.path.exists(self.file_shm):
            with open(self.file_shm, 'r') as f:
                elements = eval(f.read())
            tmpelem = elements.copy()
            for el in elements:
                if toEmpty:
                    try:
                        tmpelem.remove(el)
                        shm = shared_memory.SharedMemory(name=el)
                        shm.close()
                        shm.unlink()
                    except Exception as err:
                        pass
                else:
                    try:
                        shm = shared_memory.SharedMemory(name=el)
                        print("Shared Memory : {} = {}".format(el, bytes(shm.buf[:shm.size]).decode()))
                        shm.close()
                    except Exception as err:
                        print("Shared Memory error :", err)
                        tmpelem.remove(el)
            with open(self.file_shm, 'w') as f:
                f.write(str(tmpelem))


class ThreadDiagram(QRunnable):

    def __init__(self, name, args, n_cpu, parent=None):
        super(ThreadDiagram, self).__init__()
        self.name = name
        self.args = args
        self.pipe_exec = execution2(n_cpu)
        with open(os.path.join(os.path.expanduser('~'), '.skrypy', 'list_process.tmp'), 'w') as f:
            # list_proc = f.readlines()
            f.write('{}{}{}\n'.format('Process Name', ' '*10, 'ID'))

    def run(self):
        self.pipe_exec.go_execution(*self.args)


if __name__ == '__main__':
    self_dir_path = os.path.dirname(os.path.realpath(__file__))
    run_ssh = execution_ssh(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    os.chdir(os.path.expanduser('~'))
