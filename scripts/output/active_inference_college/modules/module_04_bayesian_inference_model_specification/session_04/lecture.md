# Bayesian Inference – Model Specification

## Learning Objectives

- Understand model comparison

---

## Introduction

Welcome back to Bayesian Inference. In our previous sessions, we’ve explored the fundamental principles of Bayesian statistics – the updating of beliefs based on evidence. We've built models, calculated prior distributions, and understood how the *prior* and *likelihood* combine to produce the *posterior* distribution. Today, we tackle a critical step in the Bayesian modeling process: model selection. We often find ourselves presented with multiple candidate models, each potentially capturing different aspects of the data. The question then arises: which model is the "best"? Simply choosing the model with the highest posterior probability isn't always the right answer. We need systematic criteria for comparing models and ultimately selecting the one that provides the most accurate representation of the underlying data-generating process. This process involves directly addressing the **model evidence**, which represents the relative support for different models.

---

## Main Topic 1: The Need for Model Comparison

The core challenge of Bayesian modeling is that the posterior probability of a model is not solely determined by its likelihood. The prior distribution reflects our initial belief in the model, and while the likelihood quantifies how well the model fits the data, these factors interact in complex ways. Consider a scenario: you’re building a model to predict customer churn. You might have two models – one very complex with many variables and another, simpler one. The simpler model might fit the current data perfectly (high likelihood), yet the complex model might have a stronger prior belief due to theoretical reasons or incorporating previously established relationships. Without a systematic way to compare these models, you risk selecting the one that merely happens to fit the current data well, rather than the one that truly explains the underlying phenomenon. Evaluating model evidence is the key to this comparison.

---

## Main Topic 2: Likelihood Ratio Tests

A foundational method for model comparison is the **Likelihood Ratio Test (LRT)**. The LRT assesses the relative support for two models, Model 1 and Model 2, by comparing their likelihoods. Specifically, we calculate the likelihood ratio:

Likelihood Ratio = P(Data | Model 2) / P(Data | Model 1)

Where:

*   P(Data | Model 1) is the likelihood of the data under Model 1.
*   P(Data | Model 2) is the likelihood of the data under Model 2.

A significant likelihood ratio indicates stronger support for Model 2.  However, LRTs have limitations. They are sensitive to model complexity; adding parameters to either model can artificially inflate the likelihood ratio, even if the new parameters aren't truly justified by the data. For instance, if you're comparing a linear regression model to one with an additional polynomial term, the polynomial term may not genuinely improve the fit, but the likelihood ratio will still favor it.

Consider this example: Imagine you are trying to model the height of students in a university. Model 1 is a simple linear regression (height ~ age). Model 2 adds a quadratic term (height ~ age + age<sup>2</sup>). The quadratic term may overfit the data, capturing noise, but the LRT might still favor Model 2 due to its higher likelihood.

---

## Main Topic 3: AIC and BIC

The Likelihood Ratio Test isn’t always practical due to the computational challenges involved in calculating likelihoods for complex models.  Therefore, we often employ approximate model selection criteria like the **Akaike Information Criterion (AIC)** and the **Bayesian Information Criterion (BIC)**. These criteria balance model fit (likelihood) with model complexity (number of parameters).

*   **AIC**:  AIC = -2 * log-likelihood + 2 * k, where *k* is the number of parameters in the model. The lower the AIC, the better the model.
*   **BIC**: BIC = -2 * log-likelihood + k * ln(n), where *n* is the number of data points.  BIC penalizes model complexity more heavily than AIC.

For example, consider a model to predict house prices. Model 1 includes square footage and number of bedrooms. Model 2 adds additional features like the age of the house and the proximity to downtown. The BIC will likely penalize Model 2 more heavily because it has more parameters, even if these parameters do provide a slight improvement in the model's fit.

---

## Main Topic 4: Interpretation of Model Evidence (Bayes Factors)

While AIC and BIC provide a convenient way to compare models, they don’t directly quantify the strength of evidence *for* one model over another. The **Bayes Factor (BF)** addresses this. The Bayes Factor is the ratio of the marginal likelihoods of two models:

BF = P(Data | Model 2) / P(Data | Model 1)

This is identical to the likelihood ratio, but explicitly recognizes the role of the prior.  A BF of 10 means that Model 2 is ten times more likely than Model 1 to have generated the observed data. BF values are interpreted as follows (approximate):

*   1 - 3: Weak evidence
*   3 - 10: Moderate evidence
*   10 - 30: Strong evidence
*   > 30: Very strong evidence

For instance, consider a clinical trial testing two drugs. Drug A has a BF of 5 compared to Drug B. This suggests there is moderate evidence to support the effectiveness of Drug A, but it's not definitive.

---

## Main Topic 5: Considerations and Caveats

Model selection is an inherently subjective process.  All criteria like AIC, BIC, and Bayes Factors rely on assumptions and approximations. Furthermore, the choice of prior distribution can significantly influence the results. It's crucial to acknowledge the limitations of these methods and to consider the broader context of the problem.  Don't solely rely on model selection criteria.  Consider the interpretability of the model, the theoretical justification for its structure, and the potential for overfitting.

For example, if you are trying to model the spread of a disease, a complex model with numerous parameters might not be appropriate if the underlying process is relatively simple.  Simplicity should sometimes be prioritized.

---

## Summary

Today’s session covered key methods for model selection within Bayesian inference. We explored the Likelihood Ratio Test, the Akaike Information Criterion (AIC), the Bayesian Information Criterion (BIC), and the concept of the Bayes Factor. Each criterion provides a different way to balance model fit and complexity. Importantly, we highlighted the crucial concept of **model evidence**, which represents the relative support for different models.  Remember, model selection is not a purely objective process; it requires careful consideration of the problem, the available data, and the broader context. The key takeaway is that systematically evaluating model evidence, rather than blindly selecting the model with the highest likelihood, is essential for building accurate and reliable Bayesian models. Moving forward, we will explore techniques for choosing appropriate priors and further refine our understanding of model selection criteria.