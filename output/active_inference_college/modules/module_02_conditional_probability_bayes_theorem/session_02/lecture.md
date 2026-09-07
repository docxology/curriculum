# Conditional Probability & Bayes’ Theorem

## Learning Objectives

- Calculate conditional probabilities

---

## Introduction

Welcome back to the course. Last week, we established the fundamental principles of probability – the likelihood of an event occurring. We explored concepts like sample spaces, events, and the rules of probability calculation. Today, we're building upon this foundation by delving into a crucial concept: **Conditional Probability**. Understanding conditional probability is paramount for reasoning under uncertainty and forming accurate beliefs based on available evidence. Essentially, it addresses the question: "What is the probability of an event occurring *given* that another event has already occurred?” This builds directly on our understanding of joint probability – the probability of two or more events happening simultaneously.

---

## Main Topic 1: Definition of Conditional Probability

The core idea of conditional probability revolves around updating our beliefs. Let’s define it formally.  If event *A* and event *B* are two events, the **conditional probability** of *A* given *B*, denoted as P(A|B), is the probability that event *A* will occur, assuming that event *B* has already happened. It represents the updated probability of *A* after observing *B*.

Mathematically, it’s calculated as:

P(A|B) = P(A ∩ B) / P(B)

Where:

*   P(A ∩ B) is the joint probability of both *A* and *B* occurring.
*   P(B) is the probability of event *B* occurring.

Crucially, P(B) must be greater than 0, otherwise the conditional probability is undefined.  This reflects the intuitive notion that you can’t condition on an event with zero probability of occurring.

Consider, for example, a medical test for a disease.  Let *A* be the event that the test comes back positive, and *B* be the event that a person actually has the disease.  The probability of a positive test result *given* that the person has the disease (P(A|B)) will be higher than the overall probability of a positive test result (P(A)), because people who have the disease are more likely to test positive.

---

## Main Topic 2: The Chain Rule and Conditional Probability

The **Chain Rule** is a powerful tool for calculating conditional probabilities, especially when dealing with multiple events. It extends the definition of joint probability to multiple events. If we have three events, *A*, *B*, and *C*, then:

P(A ∩ B ∩ C) = P(A) * P(B|C) * P(C|B) * P(B|C) * P(C)

This formula shows that the joint probability can be expressed as the product of conditional probabilities.  Let’s illustrate this with an example. Imagine a survey where individuals are asked about their preference for coffee (*A*) and their income level (*B*). We want to find the probability that someone prefers coffee *and* earns over $100,000. This can be broken down into several conditional probabilities.

Consider a different scenario: Imagine you have two coins, one fair and one biased, and you flip them both. Let *A* be the event that the fair coin lands heads, and *B* be the event that the biased coin lands heads.  We can use the chain rule to calculate the probability of both events occurring.

---

## Main Topic 3:  Examples of Conditional Probability

Let's examine several concrete examples.

1.  **Dice Roll:**  What is the probability of rolling a 6 *given* that the first roll was a 4?  Assuming a fair six-sided die, P(rolling a 6 | rolling a 4) = P(rolling a 6) / P(rolling a 4) = 1/6 / 1/6 = 1. This is because knowing the first roll was a 4 doesn’t change the probability of rolling a 6 on the next roll.

2.  **Card Drawing:** A standard deck of 52 cards. What's the probability of drawing an Ace *given* that the card is a heart? There are 13 hearts in the deck. Therefore, P(Ace | Heart) = 4/52 = 1/13.

3.  **Disease Diagnosis:** A diagnostic test for a rare disease has a 99% accuracy rate (meaning it correctly identifies those with the disease and those without). If a person tests positive, what is the probability that they actually have the disease? This requires considering the prevalence of the disease in the population – a crucial factor that influences the conditional probability. Let's assume the prevalence is 1%.  The formula becomes complex, demonstrating the importance of accurately estimating the underlying probabilities.

4.  **Weather Prediction:**  A weather service predicts a 70% chance of rain.  However, knowing that a specific weather pattern (e.g., low-pressure system) is present, the probability of rain might increase to 90%. This illustrates how new information can significantly alter our assessment.

5.  **Customer Satisfaction:** A company surveys customers about their satisfaction with a product and their purchase frequency.  They find that customers who purchase frequently (event *B*) are more likely to report high satisfaction (event *A*).

---

## Summary and Key Takeaways

Today's lecture focused on the concept of **Conditional Probability**, a fundamental tool for reasoning under uncertainty. We explored the definition of P(A|B) as P(A ∩ B) / P(B) and saw its utility in situations involving multiple events.  We illustrated this with several examples highlighting the impact of new information on our probability assessments.  Crucially, remember that P(B) must be greater than 0. The Chain Rule was introduced, allowing us to calculate joint probabilities involving multiple events.  Understanding conditional probability is vital for applications across various fields, including medicine, finance, and data analysis.  Further study and practice are highly recommended to solidify your understanding of this important concept. For instance, familiarizing yourself with Bayes' Theorem will naturally follow.