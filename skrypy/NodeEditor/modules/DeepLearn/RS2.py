class RS2_predict():
    '''
    Contains the RSS-Net framework for the task of rodent MRI skull stripping

    Note:
        link_web:  https://github.com/VitoLin21/Rodent-Skull-Stripping
                        (click Ctrl + U)
    '''
    def __init__(self, input_folder='path', output_folder='path', pretrained_model_path='path', **options):
        import subprocess

        lso = ["RS2_predict", "-i", input_folder, '-o', output_folder, '-m', pretrained_model_path]
        for ef, ev in options.items():
            if ef in ['save_probabilities', 'continue_prediction', 'verbose']:
                if ev:
                    lso.append('--' + ef)
            else:
                lso.append('-' + ef)
                lso.append(str(ev))
        command = " ".join(lso)
        print(command)
        p = subprocess.run(command, stdout=subprocess.PIPE, shell=True, check=True)
        out_txt = p.stdout.decode("utf8").splitlines()
        self.out_list = []
        for ln_txt in out_txt:
            print(ln_txt)
            if 'done with ' in ln_txt:
                self.out_list.append("{}/{}{}".format(output_folder, ln_txt[10:], "_0000.nii.gz"))
                # self.out_list.append(ln_txt[10:] + "_0000.nii.gz")

    def output_files(self: 'list_path'):
        return self.out_list
