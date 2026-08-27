class start_matlab():
    """
    docstring to be completed
    """
    def __init__(self,
                 option="enumerate(('-nodesktop','-desktop'))"):

        import matlab.engine
        self.eng = matlab.engine.start_matlab(option)

    def mat_eng(self) -> str:
        return self.eng

##############################################################################


class quit_matlab():
    """
    docstring to be completed
    """
    def __init__(self,
                 mat_eng=''):

        import matlab.engine
        mat_eng.quit()
