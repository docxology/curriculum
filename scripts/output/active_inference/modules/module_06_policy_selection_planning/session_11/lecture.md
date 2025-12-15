# Policy Selection & Planning

## Learning Objectives

- Connect to RL

---

## Introduction: Bridging Active Inference and Policy Selection

Welcome back to the Policy Selection & Planning module. In our previous sessions, we’ve established the core principles of policy optimization – iteratively refining a strategy to maximize a desired outcome. We've explored methods like Dynamic Programming and Monte Carlo Tree Search, focusing on deterministic environments and explicit value functions. However, many real-world scenarios – particularly those involving uncertainty and delayed rewards – demand a more sophisticated approach. Today, we’re going to delve into a powerful framework that tackles these challenges head-on: Reinforcement Learning (RL), and crucially, how it’s intimately linked to the concept of Active Inference.  Active Inference, in essence, provides a foundational understanding of how agents learn and make decisions by predicting their own sensory consequences – a concept that directly informs many RL algorithms. Consider a robot trying to navigate a cluttered room. It doesn’t just passively receive sensory input; it actively *predicts* how its movements will change the environment, and then adjusts its actions accordingly. This predictive element is at the heart of both Active Inference and successful RL.

---

## Main Topic 1: Reinforcement Learning – A Quick Recap

Reinforcement Learning revolves around an agent interacting with an environment. The agent observes the environment’s state, takes an action, and receives a reward (or penalty) based on the outcome. The goal is for the agent to learn a *policy* – a mapping from states to actions – that maximizes the cumulative reward over time. Let's break down the key components:

*   **Agent:** The decision-making entity.
*   **Environment:** The external system with which the agent interacts.
*   **State (s):** A snapshot of the environment’s condition.
*   **Action (a):** A choice made by the agent.
*   **Reward (r):** A scalar value indicating the desirability of the outcome.
*   **Policy (π):**  The strategy the agent uses to select actions based on the state.

There are several types of RL algorithms, each with varying levels of complexity.  Q-learning, for example, learns a Q-function which estimates the expected cumulative reward for taking a specific action in a given state.  SARSA (State-Action-Reward-State-Action) is another method that updates based on the *actual* action taken, reflecting the policy's exploration.  For instance, a dog learning to sit – the reward is positive if it successfully sits, negative if it fails. The agent adjusts its behavior to increase the probability of successful sits.

---

## Main Topic 2: Temporal Difference Learning – The Engine of RL

A cornerstone of most RL algorithms is **Temporal Difference (TD) learning**.  This method doesn’t wait until the end of an episode to evaluate an action. Instead, it learns by bootstrapping – updating value estimates based on the difference between the predicted value of the current state and the actual reward received plus the discounted estimated value of the *next* state. Imagine a student studying for an exam. They don't just rely on the final grade; they continuously assess their understanding based on practice questions and feedback. This iterative assessment – updating their knowledge based on immediate progress – mirrors the process of TD learning.  Specifically, the TD error, denoted as δ, is defined as:  δ = r + γ * V(s') - V(s) where r is the reward, γ (gamma) is the discount factor, s’ is the next state, and V(s) is the value function estimating the expected return from state s.

A common TD learning algorithm is SARSA (State-Action-Reward-State-Action-Reward). In this algorithm, the agent learns the Q-value for a specific state-action pair based on the reward received and the Q-value of the state reached after taking that action.  For example, if the agent takes action ‘A’ in state ‘S’ and receives a reward of 1 and transitions to state ‘S’ with a Q-value of 0.5, then the Q-value for the state-action pair (S, A) is updated as follows: Q(S, A) = Q(S, A) + α * (r + γ * Q(S’, A’)) where α (alpha) is the learning rate.

---

## Main Topic 3: Connecting Active Inference and RL – Predictive Coding

Now let’s connect Active Inference directly to RL. Active Inference posits that agents learn by predicting their own sensory consequences. The core idea is that the brain, and indeed any intelligent agent, constantly generates internal models of the world, predicting what its actions will *cause* to happen. These predictions are compared to actual sensory input. The difference – the error signal – is then used to update the internal model and guide future actions. This process, often called **predictive coding**, is fundamentally linked to RL.

Consider this example: a bird trying to catch a worm. The bird predicts the worm's movement based on its visual input.  If the predicted trajectory deviates from the actual movement, the bird adjusts its actions – perhaps shifting its gaze or initiating a movement – to reduce the prediction error. This ongoing feedback loop – predicting, observing, and correcting – is analogous to an RL agent seeking to maximize reward by optimizing its policy. The reward isn’t explicitly defined like in standard RL; instead, it's implicitly encoded in the minimization of the prediction error.  Furthermore, the concept of **Bayesian Active Inference** incorporates prior beliefs, allowing agents to reason about uncertainty – a crucial aspect for robust and adaptive learning in complex environments.

---

## Main Topic 4: Reward Function Design – A Critical Challenge

While TD learning provides the mechanism for learning, the success of RL heavily relies on a well-designed **reward function**. This function assigns a numerical value to each state transition, guiding the agent towards the desired behavior. Designing effective reward functions is often the most challenging aspect of RL. Poorly designed reward functions can lead to unintended behaviors. For instance, an agent tasked with cleaning a room might learn to simply push all objects into a corner – maximizing the reward for “cleaning” (defined as moving objects) rather than actually organizing them.  Consider a robot navigating a maze. If the reward is only given for reaching the end, the robot might learn to take the most direct, but potentially dangerous, route.  Reward shaping – carefully crafting the reward function to encourage specific behaviors – is a common technique, but it requires careful consideration and can still be prone to unintended consequences.

---

## Main Topic 5: Examples of RL Applications

Reinforcement Learning is being applied across a diverse range of domains.  For example, DeepMind’s AlphaGo used RL to master the game of Go, defeating the world’s best human players. This involved training an agent to play Go by rewarding it for winning and penalizing it for losing. Another example is the use of RL to control robots, allowing them to learn complex manipulation tasks. Moreover, RL is being explored in areas such as resource management, finance, and healthcare. The success of these applications highlights the power and flexibility of the RL framework.

---

## Summary – Key Takeaways

Today's session has explored the fundamental connections between Reinforcement Learning and Active Inference. We've established that:

*   Reinforcement Learning relies on TD learning, a mechanism for learning value functions through temporal difference updates.
*   Active Inference provides a foundational understanding of how agents learn by predicting their own sensory consequences.
*   The success of RL hinges on the design of effective reward functions, and the ongoing effort to bridge the gap between theoretical frameworks and practical applications.
*   The convergence of these ideas offers a promising path toward creating more intelligent and adaptive systems, capable of learning and acting in complex, uncertain environments. Further study of Bayesian Active Inference and hierarchical RL approaches will expand your understanding of this exciting field.