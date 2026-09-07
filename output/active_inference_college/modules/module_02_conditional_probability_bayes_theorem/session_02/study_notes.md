# Conditional Probability & Bayes’ Theorem - Study Notes

## Key Concepts

## Conditional Probability & Bayes’ Theorem

**Conditional Probability**: Conditional probability deals with the probability of an event occurring *given* that another event has already occurred. It’s a core concept in probability theory and statistics, allowing us to refine our understanding of likelihood based on observed information.

**Joint Probability**: Joint probability refers to the probability of two or more events happening simultaneously. It represents the likelihood of the intersection of multiple events.  Calculating joint probabilities is fundamental to understanding conditional probability.

**Conditional Probability**:  If event *A* and event *B* are two events, the **conditional probability** of *A* given *B*, denoted as P(A|B), is the probability that event *A* will occur, assuming that event *B* has already happened. It represents the updated probability of *A* after observing *B*.  Mathematically, it’s calculated as:

P(A|B) = P(A ∩ B) / P(B)

Where:

*   P(A ∩ B) is the joint probability of both *A* and *B* occurring.
*   P(B) is the probability of event *B* occurring.

Crucially, P(B) must be greater than 0, otherwise the conditional probability is undefined. This reflects the intuitive notion that you can’t condition on an event with zero probability of occurring.

**Bayes’ Theorem**: Bayes’ Theorem provides a formal method for calculating conditional probabilities. It’s derived from the definition of conditional probability and allows us to update our beliefs about an event given new evidence. The theorem is expressed as:

P(A|B) = [P(B|A) * P(A)] / P(B)

Where:

*   P(A|B) is the posterior probability of event A given event B.
*   P(B|A) is the likelihood of observing event B given that event A is true.
*   P(A) is the prior probability of event A.
*   P(B) is the probability of event B.

**Prior Probability**: Prior probability is the probability of an event occurring *before* any new evidence is considered. It represents our initial belief about the event.

**Posterior Probability**: Posterior probability is the updated probability of an event occurring *after* considering new evidence. It’s calculated using Bayes’ Theorem.

**Likelihood**: Likelihood represents the probability of observing the evidence (event B) *given* that a particular hypothesis (event A) is true. It’s one component of Bayes’ Theorem.

**Evidence**: Evidence refers to the observed data or information that is used to update our beliefs about an event. This could be a test result, a measurement, or any other form of data.

**Sample Space**: The sample space is the set of all possible outcomes of a random experiment. It represents the entire range of possibilities.

**Event**: An event is a subset of the sample space. It’s a collection of outcomes that satisfy a specific condition.  For instance, "rolling an even number on a standard six-sided die" is an event within the sample space.