# Variational Free Energy – Definition & Interpretation - Study Notes

## Key Concepts

## Variational Free Energy – Definition & Interpretation

**Free Energy**: The potential energy of a system; a measure of its stability or tendency to change. In the context of Bayesian inference, it represents the energy associated with the difference between our approximate posterior and the true posterior. A lower free energy indicates a better match.

**Variational Inference**: A technique used to approximate intractable posterior distributions in Bayesian models. Instead of directly calculating the posterior, we seek a simpler, tractable distribution that closely resembles it.

**Posterior Distribution**: The probability distribution of the model parameters given the observed data. It represents our updated beliefs about the parameters after seeing the data.

**Approximate Posterior**: A distribution that serves as an estimate of the true posterior distribution, particularly when the true posterior is too complex to calculate directly.

**Tractable Distribution**: A probability distribution that can be easily computed and manipulated mathematically, allowing us to perform calculations like integration and expectation.

**Marginal Log-Likelihood**: The logarithm of the marginal likelihood of the data, calculated with respect to the model parameters. It serves as a lower bound on the marginal log-likelihood.  Mathematically:  log P(D|θ) = Σ log P(D<sub>i</sub>|θ) – log ∫ P(D|θ) dθ

**Evidence**: The marginal likelihood of the data, representing the probability of observing the data given the model parameters. It is a critical quantity in variational inference, often denoted as E[log P(D|θ)].

**KL Divergence**: A measure of the difference between two probability distributions. In variational inference, we minimize the KL divergence between the approximate posterior and the true posterior. This represents the "distance" or difference between the two distributions. KL(q||p) = ∫ q(θ) log [q(θ) / p(θ)] dθ

**Regularization**: A technique used to prevent the approximate posterior from becoming too complex, ensuring it remains a reasonable approximation of the true posterior. Often, regularization terms are added to the optimization objective.