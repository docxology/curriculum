# Bayesian Inference – Model Specification - Study Notes

## Key Concepts

## Bayesian Inference – Model Specification

**Model Evidence**: A measure of the relative support for one model over another, given observed data. It quantifies the probability of observing the data under each model’s assumptions, taking into account both the likelihood and the model’s complexity. Higher model evidence indicates stronger support for that model.

**Likelihood Ratio Test (LRT)**: A statistical test used to compare two models by calculating the ratio of their likelihoods. A significant ratio (typically determined through a chi-squared test) suggests that one model provides a substantially better fit to the data than the other. However, LRTs are most reliable when the models share a common error structure.

**Akaike Information Criterion (AIC)**: A criterion used to compare statistical models. It balances model fit (measured by the likelihood) with model complexity (number of parameters). The AIC is calculated as: AIC = -2 * log-likelihood + 2 * k, where k is the number of parameters in the model. Lower AIC values indicate better models.

**Bayescience**: A holistic approach to scientific inquiry that emphasizes the importance of incorporating prior knowledge and subjective judgments alongside empirical evidence. It acknowledges the inherent uncertainty in scientific models and promotes a more nuanced understanding of complex systems.

**Bayesian Model Comparison**: The process of evaluating and comparing multiple candidate models to determine the most appropriate one for a given dataset. This involves quantifying the model evidence, using criteria like AIC or BIC, and considering the prior distributions.

**Bayesian Information Criterion (BIC)**:  Similar to AIC, but with a larger penalty for complexity. The BIC is calculated as: BIC = -2 * log-likelihood + k * ln(n), where n is the number of data points.  BIC favors simpler models, particularly when the sample size is large.

**Model Complexity**: The number of parameters in a statistical model. Generally, more complex models are more flexible and can fit the data more closely, but they are also more prone to overfitting.

**Prior Distributions**: Probability distributions that reflect our initial beliefs about the parameters of a model before observing any data. These priors can influence the posterior distribution and are a key element of Bayesian inference.

**Posterior Distribution**: The probability distribution of a model's parameters after observing the data, given the prior distribution and the likelihood function. It represents our updated beliefs about the model’s parameters.

**Log-Likelihood**: The natural logarithm of the likelihood function.  Working with log-likelihoods simplifies calculations and is frequently used in model comparison, as it transforms multiplicative calculations into additive ones.