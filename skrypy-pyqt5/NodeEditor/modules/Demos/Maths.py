import matplotlib.pyplot as plt
from typing import Tuple


class CerclePlot:
    """
    docstring to be completed
    """
    def __init__(self,
                 rayon=1.0,
                 centre=(0.0, 0.0)):

        self.rayon: float = rayon
        self.centre: Tuple[float, float] = centre
        self.__tracer()

    def __tracer(self) -> None:
        """Trace le cercle avec matplotlib."""
        fig, ax = plt.subplots()
        cercle = plt.Circle(self.centre, self.rayon, fill=False)
        ax.add_patch(cercle)

        ax.set_aspect('equal', adjustable='box')
        ax.set_xlim(self.centre[0] - self.rayon - 1, self.centre[0] + self.rayon + 1)
        ax.set_ylim(self.centre[1] - self.rayon - 1, self.centre[1] + self.rayon + 1)

        plt.grid()
        plt.show()
