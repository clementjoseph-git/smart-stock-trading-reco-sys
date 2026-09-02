import numpy as np

class PortfolioOptimizer:
    def __init__(self, returns, cov_matrix):
        self.returns = returns
        self.cov_matrix = cov_matrix

    def optimize(self):
        # Simplified Markowitz MPT: equally weighted portfolio
        n_assets = len(self.returns)
        weights = np.ones(n_assets) / n_assets
        return weights
