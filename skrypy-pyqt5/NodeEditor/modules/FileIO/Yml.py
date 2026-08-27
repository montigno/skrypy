class yaml_open_file():
    """
    docstring to be completed
    """
    def __init__(self,
                 yaml_file='path'):

        import yaml
        with open(yaml_file, 'r') as stream:
            self.outYaml = yaml.load(stream, yaml.FullLoader)

    def dict_yaml(self) -> dict:
        return self.outYaml

##############################################################################


class yaml_save_file():
    """
    docstring to be completed
    """
    def __init__(self,
                 yaml_file='path',
                 values_dict={}):

        import yaml
        with open(yaml_file, 'w') as stream:
            self.outYaml = yaml.dump(values_dict, stream)
            self.out_file = yaml_file

    def dict_yaml(self) -> None:
        return self.out_file

##############################################################################
