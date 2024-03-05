import numpy as np


def aobt(ytrue, ypred, alpha=2, beta=2, gamma=0, phi=0.01):
    alpha = alpha
    beta = beta
    gamma = gamma
    phi = phi
    function = []
    if len(ytrue) != len(ypred):
        print("arrays are not the same length")

    for i in range(len(ytrue)):
        # print(len(function))
        if ytrue[i] < ypred[i]:
            function.append(alpha * ((ypred[i] - ytrue[i]) ** alpha))
        elif ypred[i] < ((1 - phi) * ytrue[i]):
            function.append(
                beta * ((((1 - phi) * ytrue[i]) - ypred[i]) ** beta)
                + (gamma * ytrue[i] * phi)
            )
        elif (((1 - phi) * ytrue[i]) <= ypred[i]) and (ypred[i] <= ytrue[i]):
            function.append(gamma * (ytrue[i] - ypred[i]))
        else:
            print("Ola, cos zle!")

    return np.mean(function)
