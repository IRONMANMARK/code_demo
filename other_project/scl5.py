import numpy as np
import matplotlib.pyplot as plt


class Func():
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __add__(self, other):
        if callable(other):
            def summm(*args, **kwargs):
                return self(*args, **kwargs) + other(*args, **kwargs)
        else:
            def summm(*args, **kwargs):
                return self(*args, **kwargs) + other
        return Func(summm)

    def __sub__(self, other):
        if callable(other):
            def subbb(*args, **kwargs):
                return self(*args, **kwargs) - other(*args, **kwargs)
        else:
            def subbb(*args, **kwargs):
                return self(*args, **kwargs) - other
        return Func(subbb)

    def __mul__(self, other):
        if callable(other):
            def mult(*args, **kwargs):
                return self(*args, **kwargs) * other(*args, **kwargs)
        else:
            def mult(*args, **kwargs):
                return self(*args, **kwargs) * other
        return Func(mult)

    def __truediv__(self, other):
        if callable(other):
            def divs(*args, **kwargs):
                return self(*args, **kwargs) / other(*args, **kwargs)
        else:
            def divs(*args, **kwargs):
                return self(*args, **kwargs) / other
        return Func(divs)


class Plotter():
    def __init__(self, lower, upper, step):
        self.lower = lower
        self.upper = upper
        self.step = step
        self.result = {}

    def add_func(self, name, function):
        x = []
        y = []
        for i in np.arange(self.lower, self.upper, self.step).tolist():
            x.append(i)
            y.append(function(i))
        self.result[name] = [x, y]

    def plot(self):
        for key in self.result:
            all_result = self.result.get(key)
            x = all_result[0]
            y = all_result[1]
            plt.plot(x, y, label=key)
        plt.legend()
        plt.show()


if __name__ == "__main__":
    origin = Func(lambda x: x)
    add_two = origin - origin
    print(add_two(2))
