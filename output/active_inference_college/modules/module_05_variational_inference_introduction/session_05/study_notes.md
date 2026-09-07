# Variational Inference – Introduction - Study Notes

## Key Concepts

## Variational Inference – Introduction

**Computational Cost**: The direct calculation of the posterior distribution, *p(θ|x)*, through integration over all possible parameter values (θ) is computationally prohibitive for most realistic models due to the complexity of the integral. This integral’s difficulty scales dramatically with the number of parameters.

**Approximation Methods**: Due to the computational burden of exact inference, variational inference employs approximation techniques to estimate the posterior distribution. Instead of calculating the true posterior, we aim for a tractable distribution that closely resembles it.

**Surrogate Distributions**: Surrogate distributions are simpler probability distributions used to approximate the true posterior distribution. These distributions are designed to be computationally easy to sample from and evaluate, allowing us to perform inference efficiently. They represent a key component of variational inference, providing a practical way to handle intractable posteriors.

**Evidence Lower Bound (ELBO)**: The ELBO is a lower bound on the marginal likelihood, *p(x)*, which represents the probability of observing the data *x*. Maximizing the ELBO effectively maximizes the evidence, providing a proxy for finding the optimal parameter values.  It’s calculated as: ELBO = log(p(x)) – DKL(q||p), where DKL is the Kullback-Leibler divergence.

**Kullback-Leibler Divergence (KL Divergence)**: KL divergence measures the difference between two probability distributions, *q* and *p*, where *q* is the approximate posterior and *p* is the true posterior. Minimizing the KL divergence between the approximate distribution *q* and the true posterior *p* is a central objective in variational inference.  A smaller KL divergence indicates a better approximation.

**Factorization Assumption**:  A common assumption in variational inference is that the posterior distribution can be factorized into a product of simpler distributions. For example, the joint distribution of parameters and data might be modeled as the product of individual factor distributions. This factorization simplifies the calculation of the approximate posterior.

**Mean-Field Approximation**:  Within the factorization assumption, the mean-field approximation assumes that each factor distribution is independent of the others. This drastically reduces the complexity of the problem, though it can lead to a less accurate approximation of the true posterior.

**Marginal Likelihood**: The marginal likelihood, *p(x)*, is the probability of observing the data *x* under the model. It’s often intractable to calculate exactly, and is a critical component in the ELBO calculation. Maximizing the ELBO, which is based on the marginal likelihood, is the core of variational inference.