class numpy_reverse_list():
    """
    docstring to be completed
    """
    def __init__(self,
                 list_ndarray=[0.0]):

        import numpy as np
        self.rev = np.flipud(list_ndarray)

    def list_nd_reversed(self) -> list[float]:
        return self.rev

##############################################################################


class numpy_negative_list():
    """
    docstring to be completed
    """
    def __init__(self,
                 list_ndarray=[0.0]):

        import numpy as np
        self.rev = np.negative(list_ndarray)

    def list_nd_reversed(self) -> list[float]:
        return self.rev

##############################################################################
