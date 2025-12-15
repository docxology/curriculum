# Variational Inference - Study Notes

## Key Concepts

## Variational Inference – Study Notes

**Concept Name**: Variational Inference: A technique for approximating Bayesian inference when direct calculation of the posterior distribution is intractable. It involves representing the true posterior with a simpler, tractable distribution, minimizing the distance between them.

**Concept Name**: Evidence Lower Bound (ELF): The central principle of variational inference, aiming to find a tractable distribution `q(θ)` such that the log of its evidence provides a lower bound on the marginal likelihood `log L(θ|x)`. This lower bound allows for efficient optimization.

**Concept Name**: Marginal Likelihood: The probability of observing the data given a model and its parameters, denoted as `L(θ|x) = ∫ p(x|θ) p(θ) dx`.  This integral is often analytically intractable, driving the need for approximation techniques like variational inference.

**Concept Name**: Variational Distribution:  The approximation distribution `q(θ)` used in variational inference.  It’s chosen to be tractable, allowing for efficient computation, while still providing a reasonable estimate of the true posterior distribution.

**Concept Name**: Evidence Lower Bound Formulation: The core of variational inference, the ELF formulation uses the lower bound on the marginal likelihood, `log q(θ)`, as a target for optimization. Minimizing this lower bound effectively guides the selection of the variational distribution.

**Concept Name**: Gradient Descent: An iterative optimization algorithm commonly used to minimize the Evidence Lower Bound. It adjusts the parameters of the variational distribution to reduce the discrepancy between the approximation and the true posterior.

**Concept Name**: Optimization: The process of adjusting the parameters of the variational distribution, `q(θ)`, to minimize the Evidence Lower Bound, ultimately approximating the true posterior distribution.

**Concept Name**: Bayesian Inference: A statistical method that combines prior beliefs about parameters with observed data to produce a posterior distribution. This distribution represents our updated beliefs after considering the evidence.

**Concept Name**: Likelihood Function: `p(x|θ)`, the probability of observing the data `x` given the model parameters `θ`. It quantifies how well the model explains the observed data.

**Concept Name**: Prior Distribution: `p(θ)`, the probability distribution representing our initial belief about the model parameters `θ` before considering the data.

**Concept Name**: Evidence: The marginal likelihood `L(θ|x) = ∫ p(x|θ) p(θ) dx`. It's a measure of how well the model fits the data. Maximizing the evidence (through minimizing the ELF) is equivalent to finding the optimal parameters for the model.

**Concept Name**: Tractable: An adjective describing a distribution or calculation that is easily solved or computed, a key requirement of variational distributions.  Think of it as something that doesn't require computationally expensive techniques to handle.