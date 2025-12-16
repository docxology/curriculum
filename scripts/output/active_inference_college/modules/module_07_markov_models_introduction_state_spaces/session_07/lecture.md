# Markov Models – Introduction & State Spaces

## Learning Objectives

- Understand Markov transitions

---

## Introduction

Welcome back to our Markov Model series. Last week, we laid the groundwork by exploring discrete-time models and their application in predicting sequences. We established that these models rely on observing a series of events and then utilizing those observations to anticipate future occurrences. Our focus was on understanding how the *order* of events matters – a concept vital to building sophisticated dynamic models. Today, we delve into a fundamental principle that underpins many Markov models: the **Markov Property**. This property dramatically simplifies the analysis and construction of these models by asserting a key constraint on the system’s behavior. It's a cornerstone of their applicability across diverse fields.

---

## Main Topic 1: The Markov Property

The **Markov Property**, formally stated, asserts that the future state of a system depends *only* on its current state and not on its past history. In simpler terms, "memorylessness." This doesn’t mean a system lacks any influence from its past; rather, the influence is entirely encapsulated within the present state. Consider a simple example: predicting the weather. While past weather patterns undoubtedly influence the current weather, a Markov model built to predict tomorrow’s weather doesn’t need to track rainfall from a week ago. Instead, it focuses solely on today's conditions – sunny, cloudy, or rainy – to make its prediction.

Let’s consider a slightly more complex example: analyzing website traffic. A Markov model could track whether a user is currently viewing a product page, a category page, or the homepage. The model wouldn’t need to remember when the user last visited a particular page; it would only consider the current page type to determine the probability of the user moving to a different page. This dramatically reduces the complexity of the model.

---

## Main Topic 2: State Spaces

A central concept related to the Markov Property is the **state space**. The state space represents all possible states a system can occupy at any given time. For example, if we’re modeling the weather, the state space might consist of three states: “Sunny,” “Cloudy,” and “Rainy.” If we were modeling a simple stock price, the state space might be defined by the price at discrete intervals (e.g., $100, $101, $102...). The size of the state space directly impacts the complexity of the model. A larger state space means a larger number of possible states, increasing the number of transitions and the associated probabilities. For instance, a model tracking the stock price across a continuous range would have an infinitely large state space.

To illustrate, consider a Markov model for a customer's purchasing behavior in an online store. The state space could represent the customer’s current stage in the buying process – “Browsing,” “Added to Cart,” “Proceeding to Checkout,” or “Purchased.”  The number of states in this space defines the granularity of the model. If we only tracked these four states, we are building a relatively simple model.

---

## Main Topic 3: Transition Probabilities

The Markov property is mathematically formalized using **transition probabilities**. These probabilities quantify the likelihood of moving from one state to another in a single time step.  For example, if the current state is "Browsing," the transition probability might indicate the likelihood of the customer moving to the "Added to Cart" state. We typically represent this with a transition matrix.

Let’s assume our weather example again. We have three states: “Sunny,” “Cloudy,” and “Rainy.”  The transition matrix would show the probability of transitioning between these states. For instance, the matrix might show a 60% chance of staying "Sunny," a 20% chance of transitioning to “Cloudy,” and a 20% chance of transitioning to “Rainy.”  These probabilities are often derived from observed data, or estimated using techniques like maximum likelihood estimation.

For example, suppose we have data showing that when it’s “Sunny,” it’s 60% likely to remain “Sunny,” 20% likely to become “Cloudy,” and 20% likely to become “Rainy.” This is represented by the following transition matrix:

|          | Sunny | Cloudy | Rainy |
| :------- | :---- | :----- | :---- |
| Sunny    | 0.60  | 0.20   | 0.20  |
| Cloudy   | 0.20  | 0.50   | 0.30  |
| Rainy    | 0.20  | 0.30   | 0.50  |

---

## Main Topic 4: Examples of Markov Models

Let’s explore some concrete examples where the Markov property is applied:

1.  **Speech Recognition:** Speech recognition systems often utilize Markov models to predict the next phoneme (basic sound unit) in a spoken word, based only on the current phoneme.

2.  **Genetics:** Modeling the transmission of genetic traits across generations can be represented using a Markov model, where the state represents the genotype of an individual, and the transition probabilities reflect the likelihood of inheriting specific alleles (versions of a gene).

3.  **Queueing Theory:**  In operations research, Markov models are used to analyze waiting lines (queues), assuming that the number of customers in the queue at any given time depends only on the current number and not on the queue's history.  Consider a call center: the number of callers waiting currently depends only on the arrival rate and service rate—not on how long people were waiting previously.

4.  **PageRank Algorithm (Google):** Google’s original PageRank algorithm, which determined the importance of web pages, leveraged a Markov model where the state represents a webpage and the transition probabilities represent the likelihood of a user clicking a link from one page to another.

5. **Gambit Theory:**  Models of card games such as Blackjack utilize Markov models to determine probabilities of card draws, using only the current hand as input.

---

## Summary

Today’s lecture centered around the **Markov Property**, a cornerstone of Markov models. We established that the future state of a system depends solely on its current state, eliminating the need to track past history. We defined the **state space** – all possible states the system can occupy. Crucially, we examined **transition probabilities**, which quantify the likelihood of moving between states.  We explored various applications, including speech recognition, genetics, queueing theory, and Google’s PageRank algorithm, highlighting the broad applicability of this fundamental concept.  Understanding the Markov property is essential for building and interpreting these powerful dynamic models. Next time, we will delve deeper into calculating and interpreting these transition probabilities.