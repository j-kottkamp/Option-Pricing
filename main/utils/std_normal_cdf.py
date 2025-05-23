from imports import np, math

def standard_normal_cdf(x):
    return 0.5 * (1 + math.erf(x / np.sqrt(2)))