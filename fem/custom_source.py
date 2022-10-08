from fenics import UserExpression
import FESTIM as F


class InterpolatedExpression(UserExpression):
    def __init__(self, f) -> None:
        super().__init__()
        self.f = f

    def eval(self, value, x):
        r = (x[0]**2 + x[1]**2)**0.5
        z = x[2]
        value[0] = self.f(r, z)

    def value_shape(self):
        # scalar value
        return ()


class InterpolatedSource(F.Source):
    def __init__(self, f, volume, field) -> None:
        value = InterpolatedExpression(f)
        super().__init__(value, volume, field)


if __name__ == "__main__":
    def f(x, y, z):
        return x + y + z

    my_source = InterpolatedExpression(f)
    print(my_source((1, 2, 3)))
