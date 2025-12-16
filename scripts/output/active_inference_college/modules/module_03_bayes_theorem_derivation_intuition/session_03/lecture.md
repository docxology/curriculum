# Bayes’ Theorem – Derivation & Intuition

## Learning Objectives

- Understand the derivation

---

## Introduction

Welcome back to Bayesian Inference – a cornerstone of modern statistical analysis. In our previous sessions, we’ve established the fundamental principles of Bayesian reasoning and introduced the concept of prior probabilities. Recall that Bayesian inference revolves around updating our beliefs about an event based on new evidence.  We’ve seen how prior probabilities represent our initial beliefs *before* observing any data.  Today, we’ll delve into the heart of Bayesian inference: Bayes’ Theorem. This theorem provides a rigorous mathematical framework for quantifying this updating process.  At its core, Bayes’ Theorem allows us to move from our prior belief about an event to a posterior belief, given observed data.  Think of it like refining your estimate based on new information – a process we all engage in daily, albeit often subconsciously.  We’ll move from intuitive understanding to a formal derivation, solidifying your grasp of this vital tool.

---

## Main Topic 1: Conditional Probability Revisited

Before diving into Bayes' Theorem, we need a firm understanding of **conditional probability**. **Conditional Probability**: The probability of an event occurring given that another event has already occurred. We denote this as P(A|B), read as “the probability of A given B”. The key to understanding conditional probability is recognizing that the occurrence of event B *changes* the probability landscape for event A.

Consider a simple example: Suppose we know that it is raining (event A). What is the probability that the ground is wet (event B)?  This is influenced by whether it is raining, but also potentially by whether someone has just washed their car.  The formula for conditional probability is:

P(A|B) = P(A ∩ B) / P(B)

Where:
*   P(A ∩ B) is the probability of both A and B occurring.
*   P(B) is the probability of event B occurring.

This concept is absolutely crucial because Bayes’ Theorem directly relies on calculating conditional probabilities. Let's consider an example. A medical test for a rare disease yields a positive result. What is the probability that a person actually has the disease, given the positive test result? This is a classic application of conditional probability, and we’ll see it explicitly within the derivation of Bayes’ Theorem.

---

## Main Topic 2: Derivation Steps

Now, let’s formally derive Bayes’ Theorem. The theorem itself expresses the relationship between the prior probability, the likelihood, and the posterior probability. We start with the fundamental definition of conditional probability, then utilize the definition of likelihood to build the theorem.

Let’s define our events as follows:

*   A: The event we’re interested in.
*   B: Some observed evidence.

Bayes’ Theorem is expressed as:

P(A|B) = [P(B|A) * P(A)] / P(B)

Where:

*   P(A|B): Posterior Probability – The probability of event A occurring given that event B has occurred. This is what we’re ultimately trying to calculate.
*   P(B|A): Likelihood – The probability of observing evidence B given that event A is true. This measures how well the data supports the hypothesis.
*   P(A): Prior Probability – Our initial belief in the probability of event A occurring *before* observing any data.
*   P(B): Marginal Likelihood – The probability of observing evidence B, regardless of whether event A is true or not.  It’s often calculated as the sum of probabilities of B occurring under both A being true and A being false.  (P(B) = P(B|A)P(A) + P(B|¬A)P(¬A))

Let’s walk through an example to illustrate this. Suppose we have a diagnostic test for a disease. The test has a sensitivity of 95% (P(B|A)), meaning that if a person has the disease (A), the test will correctly identify it 95% of the time. The prevalence of the disease in the population is 1% (P(A)). We want to calculate the probability that a person actually has the disease given a positive test result (P(A|B)).

---

## Main Topic 3: Applying Bayes' Theorem – The Medical Test Example

Using Bayes' Theorem with our medical test example:

*   P(A) = 0.01 (Prevalence of the disease)
*   P(B|A) = 0.95 (Sensitivity of the test)
*   P(¬A) = 0.99 (Probability of not having the disease)

We want to find P(A|B).  We know that P(¬A|¬B) = 0.99.  Therefore, P(B|¬A) = 1 - P(¬B|¬A) = 1 - 0.95 = 0.05 (Specificity of the test).

Plugging these values into Bayes’ Theorem:

P(A|B) = [P(B|A) * P(A)] / P(B)

First, we need to calculate P(B). We can do this using the law of total probability:

P(B) = P(B|A) * P(A) + P(B|¬A) * P(¬A)
P(B) = (0.95 * 0.01) + (0.05 * 0.99)
P(B) = 0.0095 + 0.0495
P(B) = 0.059

Now, we can calculate P(A|B):

P(A|B) = (0.95 * 0.01) / 0.059
P(A|B) = 0.0095 / 0.059
P(A|B) ≈ 0.161

This result demonstrates that even with a highly sensitive test, the probability of actually having the disease given a positive result is relatively low, due to the low prevalence of the disease in the population.  This highlights the importance of considering prior probabilities.  Consider a disease that is extremely rare – even a 99% accurate test will still produce false positive results.

---

## Summary and Key Takeaways

Today’s session focused on the derivation and interpretation of Bayes’ Theorem. We revisited conditional probability, formally defined the components of Bayes' Theorem – Prior (P(A)), Likelihood (P(B|A)), and Posterior (P(A|B)), and demonstrated its application using a classic medical test example. The key takeaway is that Bayes’ Theorem provides a framework for updating our beliefs based on new evidence. It’s not just a mathematical formula; it’s a powerful tool for reasoning under uncertainty. The theorem emphasizes the interplay between prior knowledge and observed data.  Furthermore, we stressed that the choice of prior probability can significantly influence the posterior probability.  Understanding Bayes' Theorem is fundamental to Bayesian inference and its widespread applications in fields ranging from medicine and finance to artificial intelligence and machine learning.  Continue to explore the implications of this core statistical concept.