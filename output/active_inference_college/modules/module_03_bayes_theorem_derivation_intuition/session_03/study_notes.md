# Bayes’ Theorem – Derivation & Intuition - Study Notes

## Key Concepts

## Bayes’ Theorem – Derivation & Intuition

**Introduction**

Welcome back to Bayesian Inference – a cornerstone of modern statistical analysis. In our previous sessions, we’ve established the fundamental principles of Bayesian reasoning and introduced the concept of prior probabilities. Recall that Bayesian inference revolves around updating our beliefs about an event based on new evidence. We’ve seen how prior probabilities represent our initial beliefs *before* observing any data. Today, we’ll delve into the heart of Bayesian inference: Bayes’ Theorem. This theorem provides a rigorous mathematical framework for quantifying this updating process. At its core, Bayes’ Theorem allows us to move from our prior belief about an event to a posterior belief, given observed data. Think of it like refining your estimate based on new information – a process we all engage in daily, albeit often subconsciously. We’ll move from intuitive understanding to a formal derivation, solidifying your grasp of this vital tool.

**Key Concepts**

**Prior**: Prior The probability distribution of a hypothesis before any evidence is considered. It represents our initial belief about the likelihood of an event occurring.  It’s often denoted as P(H) where H is the hypothesis. *Mnemonic: Prior = "First Belief"*

**Likelihood**: Likelihood The probability of observing the data (evidence) given that the hypothesis is true. It measures how well the data supports a specific hypothesis. It’s commonly represented as P(Data | H). *Mnemonic: Likelihood = "Link Data to Hypothesis"*

**Posterior**: Posterior The updated probability distribution of a hypothesis after observing the data. It reflects our revised belief about the hypothesis, taking into account the evidence. It’s denoted as P(H | Data). *Mnemonic: Posterior = "Post-Evidence Belief"*

**Bayes' Theorem**: Bayes’ Theorem:  A mathematical equation that describes how to update our beliefs in light of new evidence. It’s expressed as:

P(H | Data) = [P(Data | H) * P(H)] / P(Data)

Where:
*   P(H | Data) is the posterior probability of the hypothesis given the data.
*   P(Data | H) is the likelihood – the probability of observing the data given the hypothesis.
*   P(H) is the prior probability of the hypothesis.
*   P(Data) is the probability of observing the data (often a normalizing constant).

**Probability**: Probability: A numerical representation of the likelihood of an event occurring. It ranges from 0 (impossible) to 1 (certain).

**Normalization**: Normalization: The process of ensuring that the sum of probabilities in a probability distribution equals 1.  The term P(Data) in Bayes’ Theorem performs this crucial role.

**Conditional Probability**: Conditional Probability: The probability of an event occurring given that another event has already occurred. We denote this as P(A|B), read as “the probability of A given B”. The key to understanding conditional probability is recognizing that the occurrence of event B *changes* the probability landscape for event A.

Consider a simple example: Suppose we know that it is raining (event A). What is the probability that the ground is wet (event B)? This is influenced by whether it is raining, but also potentially by whether someone has just washed their car. The formula for conditional probability is:

P(A|B) = P(A ∩ B) / P(B)

Where:
*   P(A ∩ B) is the probability of both A and B occurring.
*   P(B) is the probability of event B occurring.

**Chain Rule**: Chain Rule: A rule in probability that allows us to calculate the probability of multiple dependent events. It's particularly relevant in Bayesian inference when dealing with complex models.

**Evidence (P(Data))**: Evidence: The probability of observing the data, regardless of the hypothesis. It acts as a normalizing constant, ensuring that the posterior probability is a valid probability.  Often calculated as the sum of P(Data | H) * P(H) over all possible hypotheses.