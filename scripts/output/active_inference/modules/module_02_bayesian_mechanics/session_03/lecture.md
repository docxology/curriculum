# Bayesian Mechanics

## Learning Objectives

- Calculate posterior distributions

---

## Introduction

Welcome back to Bayesian Mechanics. In our previous session, we established the fundamental principles of probability – likelihood, prior, and evidence – setting the stage for understanding Bayesian inference. Recall that probability, at its core, describes the likelihood of an event occurring. However, probabilistic reasoning can be influenced by pre-existing beliefs. Bayesian inference provides a formalized method to update these beliefs in light of new evidence. This session will focus on calculating posterior distributions, the central outcome of this process. We’ll explore how prior beliefs interact with observed data to arrive at a refined understanding. Consider the scenario of estimating the lifespan of a machine. Initial observations might suggest a lifespan of 5 years, influenced by past experiences. However, a sudden, significant failure could drastically alter this initial estimate. Bayesian inference provides a systematic way to incorporate this new information.

---

## Main Topic 1: Bayes’ Theorem – The Foundation

At the heart of Bayesian inference lies Bayes’ Theorem, a mathematical formula that expresses the conditional probability of an event given another event. Let's define the key components:

*   **Prior Probability (P(A))**: This represents our initial belief about the probability of an event *A* occurring before observing any new data. It’s our subjective assessment, based on experience, expert opinion, or simply a starting assumption.
*   **Likelihood (P(B|A))**: This quantifies the probability of observing data *B* given that event *A* is true. It’s the probability of the data, assuming the event *A* is correct.
*   **Posterior Probability (P(A|B))**: This is the updated probability of event *A* occurring after considering the observed data *B*. It represents our revised belief.

Bayes’ Theorem is expressed as follows:

**P(A|B) = [P(B|A) * P(A)] / P(B)**

Where P(B) is the evidence or marginal probability of observing the data *B*, often calculated as a normalizing constant to ensure the posterior probabilities sum to 1.  Let's break down how this equation represents the inference process. Imagine we’re trying to determine if a coin is biased. Our prior belief about the bias (P(A)) might be that it’s a fair coin (50/50). Then, we flip the coin 10 times and get 7 heads. The likelihood, P(B|A), is the probability of getting 7 heads out of 10 flips if the coin *is* fair. The posterior probability, P(A|B), is our updated belief about the coin's fairness after observing the data.

---

## Main Topic 2: Calculating Posterior Distributions

Calculating the posterior distribution is the core task of Bayesian inference. Instead of a single point estimate, we obtain a probability distribution representing our belief about the possible values of the parameter (in our coin example, the probability of heads).  This distribution reflects the uncertainty inherent in the process.

Consider a simple example: We want to estimate the proportion of defective items in a production batch. We can represent this with a single parameter, *θ* (theta), the proportion of defective items.

*   **Prior:** We might start with a uniform prior, assuming we have no initial information about the defect rate, i.e., P(θ) = 1 for 0 ≤ θ ≤ 1.
*   **Likelihood:** Let's say we inspect 10 items and find 6 to be defective. The likelihood function, P(data | θ) , would be based on the binomial distribution.
*   **Posterior:** The posterior distribution, P(θ | data), will be a Beta distribution. The Beta distribution is specifically chosen because it is conjugate to the Binomial distribution, simplifying the calculation.

The Beta distribution is defined by two shape parameters, α and β.  In this case, α = 6 + 1 = 7 and β = 1 + 10 = 11, representing the number of observed successes (defective items) plus one, and the number of observed failures plus one, respectively.  This demonstrates a key aspect: the data influences the shape of the posterior distribution.

---

## Main Topic 3: More Concrete Examples

Let’s explore some further examples to solidify the concept.

1.  **Medical Diagnosis**: A doctor is trying to diagnose a patient based on a test result. The prior probability of a disease is based on the prevalence in the population. The likelihood is the probability of observing a positive test result given the disease. The posterior probability becomes the updated probability of having the disease.
2.  **Machine Failure**:  As previously discussed, we can estimate the failure rate of a machine using Bayes’ Theorem. The prior could represent our belief based on the machine’s age or design. The likelihood depends on the observed failures during operation.
3.  **A/B Testing**: A company wants to determine whether a new marketing campaign is more effective than the old one. The prior could be based on historical data. The likelihood is the probability of observing higher conversion rates with the new campaign.
4. **Spam Detection**: A spam filter uses Bayesian inference to classify emails. The prior might reflect the general spam rate. The likelihood is the probability of an email being spam given its features. The posterior probability is the updated probability of an email being spam.
5.  **Gene Expression Analysis**: A researcher analyzes gene expression data to identify potential biomarkers. The prior reflects existing knowledge about gene expression patterns. The likelihood is the probability of observing specific expression levels given a particular gene variant. The posterior probability is the updated probability of a gene variant being associated with a disease.

---

## Main Topic 4:  Assumptions and Limitations

It's crucial to acknowledge the assumptions and limitations of Bayesian inference. The process relies heavily on the accuracy of the prior distribution. A biased prior can significantly influence the posterior, even with abundant data. Furthermore, calculating the evidence (P(B)) – the normalizing constant – can be computationally challenging, especially in high-dimensional spaces. Methods like Markov Chain Monte Carlo (MCMC) sampling are often employed to approximate the posterior distribution. Finally, it is important to note that Bayesian inference is a subjective process, influenced by the choice of prior.

---

## Summary

In this session, we’ve covered the fundamental concepts of Bayesian inference, focusing on Bayes’ Theorem and the calculation of posterior distributions. We learned that:

*   Bayes’ Theorem provides a framework for updating beliefs based on new evidence.
*   The posterior distribution represents our updated belief about a parameter, reflecting both prior knowledge and observed data.
*   The choice of prior is a crucial step, impacting the shape and interpretation of the posterior.
*   Bayesian inference is a powerful tool for decision-making in situations with uncertainty.  We also discussed several illustrative examples to demonstrate the application of this powerful method.  In our next session, we will delve deeper into the practical aspects of Bayesian inference, including MCMC sampling techniques for approximating posterior distributions and tackling more complex scenarios.