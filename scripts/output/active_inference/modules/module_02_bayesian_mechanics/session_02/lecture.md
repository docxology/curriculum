# Bayesian Mechanics

## Learning Objectives

- Understand probability distributions

---

## Introduction

Welcome back to Bayesian Mechanics. Last week, we established the foundational principles of Bayesian inference – reasoning under uncertainty using prior beliefs and observed data. This session builds directly on that, focusing on the bedrock of probabilistic modeling: probability theory. Specifically, we’ll revisit key probability concepts, including joint probability, marginal probability, and, crucially, Bayes’ Theorem. Our aim is to solidify your understanding of these concepts, as they are absolutely essential for effectively applying Bayesian mechanics. Many of the techniques we'll explore later rely heavily on a firm grasp of these fundamentals. Consider this session a critical reinforcement of your statistical toolkit.

---

## Main Topic 1: Joint Probability

At its core, probability describes the likelihood of an event occurring. However, the world is rarely simple. Often, multiple events are linked, and we need a way to quantify the probability of them *both* happening. This is where **joint probability** enters the picture.

**Joint Probability**: The probability of two or more events occurring simultaneously.  It’s represented as P(A, B), P(A, B, C), and so on, indicating the probability of all specified events occurring together.

Let’s consider a simple example. Imagine flipping a fair coin twice. The possible outcomes are HH, HT, TH, and TT. We can assign a probability to each outcome. However, we're interested in the probability of getting heads on the first flip *and* tails on the second flip, represented as P(Heads, Tails).  Since the flips are independent, this probability is simply the product of the individual probabilities: P(Heads) * P(Tails) = (1/2) * (1/2) = 1/4.

Another example: Imagine we have two dice.  We want to find the probability of rolling a 3 on the first die *and* a 6 on the second die. This is P(3, 6). There are 36 possible outcomes when rolling two dice (6 x 6). Only one of these outcomes satisfies our condition (3, 6). Therefore, P(3, 6) = 1/36.

---

## Main Topic 2: Marginal Probability

Now, let's move on to **marginal probability**.  This concept allows us to calculate the probability of a single event, even when we’re considering the joint probability of multiple events.

**Marginal Probability**: The probability of a single event, calculated by summing the probabilities of all possible combinations of events that lead to that outcome.  It’s a way of “averaging” over the joint probabilities.

Let’s return to our coin flipping example. We calculated P(Heads, Tails) = 1/4.  We can use marginal probability to find the probability of simply getting heads on a single flip – P(Heads). This is done by summing the joint probabilities of all the outcomes where heads appears:  P(Heads) = P(Heads, Heads) + P(Heads, Tails) + P(Heads, Tails) + P(Heads, Tails) = 1/4 + 1/4 = 1/2.

Consider this scenario: We have a bag containing 5 red balls and 5 blue balls. We draw one ball at random. What is the probability that it’s red? This is P(Red). We can calculate this by considering all the possible joint probabilities of drawing a red ball in combination with any other event (which is just the initial state of the bag). In this simple case, P(Red) = 5/10 = 1/2.

---

## Main Topic 3: Bayes’ Theorem

Finally, we arrive at the central concept of this session: **Bayes’ Theorem**. This theorem provides the mathematical framework for updating our beliefs based on new evidence.

**Bayes’ Theorem**: A mathematical formula that allows us to calculate the posterior probability of an event given prior beliefs and new evidence. It's formally expressed as:

P(A|B) = [P(B|A) * P(A)] / P(B)

Where:

*   P(A|B): Posterior Probability – The probability of event A occurring given that event B has occurred.
*   P(B|A): Likelihood – The probability of observing event B given that event A has occurred.
*   P(A): Prior Probability – Our initial belief about the probability of event A occurring.
*   P(B): Evidence – The probability of observing event B.  (Often calculated as a normalizing constant).

Let’s illustrate with an example. Imagine a medical test for a rare disease. The disease affects 1% of the population. The test has a sensitivity of 95% (meaning it correctly identifies those with the disease) and a specificity of 90% (meaning it correctly identifies those without the disease). A person tests positive. What is the probability that they actually have the disease?

This is a classic application of Bayes’ Theorem. Let:

*   A: The person has the disease.
*   B: The test result is positive.

We know:

*   P(A) = 0.01 (Prior probability of having the disease)
*   P(B|A) = 0.95 (Likelihood of a positive test given they have the disease)
*   P(B|¬A) = 0.05 (False positive rate -  likelihood of a positive test given they *don't* have the disease)

Calculating P(A|B) using Bayes' Theorem gives us a posterior probability significantly higher than the initial 1%, reflecting the increased confidence due to the positive test result.

---

## Summary

In this session, we’ve revisited and solidified our understanding of several key probabilistic concepts. We’ve explored: joint probability, the essence of understanding the simultaneous occurrence of events; marginal probability, a method for calculating probabilities of individual events; and crucially, Bayes’ Theorem. This theorem provides the means to refine our initial beliefs in light of new data.  Remember, Bayesian mechanics isn’t about simply calculating probabilities; it’s about continuously updating our understanding of the world based on observed evidence. Mastering these foundational concepts is paramount for success in subsequent modules. The ability to correctly apply Bayes' Theorem will be a cornerstone of your analytical capabilities. Finally, consider this: the application of probability theory, especially when combined with Bayesian reasoning, can be found in many real-world applications, from medical diagnostics to engineering design.