class numpy_hyperbolic():
    """
    docstring to be completed
    """
    def __init__(self,
                 x=[0.0],
                 op="enumerate(('sinh', 'cosh', 'tanh', 'arcsinh', 'arccosh', 'arctanh'))"):

        import numpy as np
        x = np.array(x)
        self.res = getattr(np, op)(x)

    def res(self) -> list[float]:
        return self.res

##############################################################################
