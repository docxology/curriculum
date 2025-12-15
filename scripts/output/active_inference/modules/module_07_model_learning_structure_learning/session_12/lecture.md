# Model Learning & Structure Learning

## Learning Objectives

- Learn model parameters

---

## Introduction: Connecting Prior Knowledge to Parameter Estimation

Welcome back to our exploration of Model Learning & Structure Learning. Last week, we discussed the fundamental principle of learning from data – how a model adapts its representation of the world to better fit observed patterns. We established the core idea of a model as a mathematical abstraction designed to explain and predict phenomena. Now, we shift our focus to *how* we determine the specific values within that model – the process of **parameter estimation**. This is arguably the most critical step in building a useful model, as the parameters dictate the model’s behavior and predictive power. Think of it like tuning an instrument; adjusting the parameters allows you to refine the model’s output until it best reflects the underlying data. We will begin by exploring the overarching goal of parameter estimation, before diving into the mechanics of a widely used technique: Maximum Likelihood Estimation.

---

## Main Topic 1: The Goal of Parameter Estimation

Parameter estimation is the process of finding the best values for the parameters within a given model, given a set of observed data. These parameters, represented typically by Greek letters (θ), define the relationships within the model. For instance, if we’re modeling the growth of a population, parameters might include birth rate, death rate, and carrying capacity. The accuracy of our model, and therefore its ability to make predictions, hinges on the accuracy of these parameter values. A poorly estimated model will generate inaccurate forecasts, while a well-estimated model will provide valuable insights. Consider a simple linear regression model: the parameters are the slope (β) and the intercept (α).  The goal of parameter estimation is to find the β and α that minimize the difference between the model's predictions and the actual observed data.  The inherent uncertainty in our data and the complexity of the model mean that parameter estimation is rarely, if ever, a perfectly precise process. Instead, we aim for the *best* estimate, acknowledging the associated uncertainties. Another way to view this is through an analogy to adjusting a camera's focus; we continually tweak the parameters until the resulting image is sharpest.

---

## Main Topic 2: Maximum Likelihood Estimation (MLE) – The Core Technique

**Maximum Likelihood Estimation (MLE)** is the most prevalent method for parameter estimation. The central idea behind MLE is remarkably intuitive: we want to find the parameter values that make the observed data *most probable*.  More formally, we are seeking the values of θ that maximize the **likelihood function**. The likelihood function, denoted L(θ), represents the probability of observing the data given a specific set of parameter values. Let's say we have a dataset of n independent and identically distributed (i.i.d.) observations.  The likelihood function is calculated by multiplying the probability density function (PDF) or probability mass function (PMF) for each observation, assuming we know the underlying distribution of the data. For example, if our data follows a normal distribution, L(θ) would be the product of the normal PDF values for each data point, evaluated at the given θ values. If our data is discrete, the likelihood is simply the product of the probabilities for each observed value. The mathematical crux is finding the θ that makes L(θ) as large as possible. This is typically achieved through calculus, finding the critical points of the likelihood function. This means finding where the derivative of L(θ) with respect to θ equals zero.  For instance, in a simple binomial model (representing coin flips), maximizing the likelihood function will yield the most likely probability of heads.

---

## Main Topic 3: The Likelihood Function – A Deeper Dive

The likelihood function isn’t just a mathematical construct; it’s a direct reflection of our confidence in the model. A high likelihood value indicates that the data we’ve observed is consistent with the model's parameters. Conversely, a low likelihood value suggests that the model is a poor fit for the data.  Consider modelling the number of customers arriving at a store each hour. We might assume a Poisson distribution. The likelihood function would be the product of the Poisson PMFs, each evaluated at a particular expected arrival rate (a parameter). The higher the expected arrival rate, the greater the likelihood, *assuming* the Poisson distribution accurately models the process. In practice, we often use iterative numerical optimization algorithms (like Newton-Raphson or Gradient Descent) to find the parameter values that maximize the likelihood function, as analytical solutions are often unavailable. Moreover, the likelihood function is often used to construct confidence intervals for the parameters.

---

## Main Topic 4:  Examples of Parameter Estimation

Let's examine some concrete examples. **Consider** a simple exponential decay model used to describe the decline of a radioactive substance. The parameter is the decay constant (λ). We are given a set of measurements of the remaining amount of the substance at different times. The goal is to estimate λ. The likelihood function would be the product of the exponential PDFs, each evaluated at a particular value of λ. **Imagine**, we have data on the daily sales of a product. We might use a normal distribution to model the sales. The parameters are the mean (μ) and standard deviation (σ).  **For instance**, in a medical study, we might be modeling the time it takes patients to recover from an illness. The parameter is the recovery rate. **Such as** analyzing data from a clinical trial, the parameter might be the effect size of a drug. **Moreover**, in finance, we can model stock prices using an ARIMA model and estimate parameters like the autoregressive coefficients (AR). **Think** about predicting house prices – we can estimate parameters related to square footage, number of bedrooms, and location. Finally, **consider** estimating the rate of infection spread in a population - the reproduction number (R₀) is a key parameter.

---

## Main Topic 5: Bayesian Updating of Models

While MLE focuses on maximizing the likelihood, **Bayesian Updating** incorporates prior beliefs about the parameters.  Bayesian estimation uses Bayes' Theorem to update our belief about the parameters given the observed data.  The formula is:

P(θ | Data) = [P(Data | θ) * P(θ)] / P(Data)

Where:

*   P(θ | Data) is the posterior distribution – our updated belief about the parameters after seeing the data.
*   P(Data | θ) is the likelihood function (same as in MLE).
*   P(θ) is the prior distribution – our initial belief about the parameters.
*   P(Data) is the marginal likelihood or evidence, a normalizing constant.

The prior distribution reflects any existing knowledge or assumptions we have about the parameters before seeing the data. This is a crucial difference between MLE and Bayesian estimation. For example, if we have no prior knowledge about the decay constant of a radioactive substance, we might use a uniform prior – assigning equal probability to all possible values.

---

## Summary

Today’s lecture has covered the core concepts of parameter estimation. We established that parameter estimation is the process of finding the best values for the parameters within a model, given observed data. We delved into Maximum Likelihood Estimation (MLE), the most common technique, which involves maximizing the likelihood function. We explored the importance of the likelihood function as a measure of confidence in the model.  We briefly introduced Bayesian updating, highlighting its incorporation of prior beliefs.  The key takeaways are:  Parameter estimation is a cornerstone of model building; MLE offers a powerful method for finding parameter values; and understanding the underlying principles of the likelihood function and Bayesian updating are crucial for building robust and reliable models. The next session will build upon this foundation by examining different methods for optimizing the likelihood function and evaluating the uncertainty in parameter estimates.