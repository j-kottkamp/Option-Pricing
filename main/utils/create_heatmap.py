from imports import np
from models.bsm import BSMModel


def create_heatmap_matrix(S, K, T, r, sigma, index, columns, x_min, x_max, y_min, y_max):
    params = {
        "Spot Price": S,
        "Strike Price": K,
        "Time to Maturity": T,
        "Volatility (σ)": sigma,
        "Risk-Free Rate": r
    }
    
    param_map = {
        "Spot Price": "S",
        "Strike Price": "K",
        "Time to Maturity": "T",
        "Volatility (σ)": "sigma",
        "Risk-Free Rate": "r"
    }

    x_key = index
    y_key = columns

    x = np.linspace(x_min, x_max, 10)
    y = np.linspace(y_min, y_max, 10)

    matrix_shape = (len(y), len(x))
    options = ["call", "put"]
    matrices = np.zeros((2, *matrix_shape))  # shape: (2, len(y), len(x))

    for n, option in enumerate(options):
        matrix = np.zeros(matrix_shape)
        for i, x_val in enumerate(x):
            for j, y_val in enumerate(y):
                args = {
                    param_map[k]: v for k, v in params.items()
                }
                args[param_map[x_key]] = x_val
                args[param_map[y_key]] = y_val

                model = BSMModel(**args)
                price = model.price_option(option)

                matrix[j, i] = price
        matrices[n] = matrix

    return matrices, x, y
    
if __name__ == "__main__":
    create_heatmap_matrix(100, 100, 1, 0.05, 0.2, "Spot Price", "Volatility (σ)", 80, 120, 0.25, 0.75)