# Variational Inference - Study Notes

## Key Concepts

## Study Notes: Variational Inference – Core Concepts

**Concept Name**: Bayesian Inference: Bayesian inference is a statistical method that updates beliefs about a parameter (or set of parameters) based on observed data. It uses Bayes’ Theorem to calculate the posterior probability, representing the updated belief after considering the data.

**Concept Name**: Bayes’ Theorem: Bayes’ Theorem is a fundamental equation in probability theory used to update our beliefs. It relates the prior probability of a hypothesis to the probability of observing the evidence, given the hypothesis. Mathematically: P(θ|X) = [P(X|θ) * P(θ)] / P(X)

**Concept Name**: Evidence Lower Bound (ELBO): The Evidence Lower Bound is a key component of variational inference. It’s a lower bound on the marginal likelihood, which is the probability of observing the data. Maximizing the ELBO provides an approximation to the true posterior. The ELBO is expressed as: ELBO = E[log P(X, θ)] - KL(Q(θ)|P(θ))

**Concept Name**: KL Divergence: KL Divergence (Kullback-Leibler Divergence) measures the difference between two probability distributions. It quantifies how much information is lost when one distribution (Q, the approximate posterior) is used to approximate another (P, the true posterior). It is always non-negative and is maximized when the two distributions are identical.

**Concept Name**: Approximate Posterior: In variational inference, we don't directly compute the true posterior distribution, P(θ|X), which is often intractable. Instead, we approximate it with a simpler, tractable distribution, Q(θ). This Q(θ) is the approximate posterior.

**Concept Name**: Mean Field Approximation: The Mean Field Approximation simplifies the approximate posterior by assuming that the parameters within a complex model are independent of each other. This significantly reduces the complexity of the approximation, allowing for tractable calculations. This is a crucial step in making the problem solvable.

**Concept Name**: Marginal Likelihood: The marginal likelihood, or evidence, P(X) represents the probability of observing the data. It’s a normalizing constant in Bayes’ Theorem and is often the most challenging part of Bayesian inference to compute directly. Variational inference aims to maximize the Evidence Lower Bound (ELBO), which is a lower bound on this.

---

**Additional Points & Elaboration:**

*   **Why Approximation?** The high dimensionality of many probability distributions makes direct computation of the posterior intractable.  The integral in Bayes’ Theorem becomes impossible to solve analytically in most cases.
*   **Tractability:** The goal of variational inference is to find a Q(θ) that’s easy to work with – meaning we can easily calculate its expected value and its KL divergence.
*   **Maximization:** We maximize the ELBO with respect to the parameters of the approximate posterior Q(θ). This corresponds to finding the Q(θ) that best resembles the true posterior.
*   **Iterative Process:** The process of maximizing the ELBO is often iterative, involving updates to Q(θ) until convergence.
*   **Simplifications:** The Mean Field Approximation is one way to drastically simplify the problem, but other approximations exist depending on the model’s structure.