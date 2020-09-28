import numpy as np
import math

def roaming_entropie(x):
    length = x.shape[0]
    p = np.zeros(length)
    sum = np.sum(x)
    if sum > 0:
        for i in range(length):
            p[i] = x[i] / sum
            if p[i] != 0:
                p[i] = p[i] * math.log(p[i])

        re = -1 * np.sum(p) / math.log(length)
        return re
    else:
        return 0