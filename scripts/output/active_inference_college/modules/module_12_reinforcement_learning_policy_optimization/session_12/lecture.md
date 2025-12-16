# Reinforcement Learning – Policy Optimization

## Learning Objectives

- Understand MDPs

---

## Introduction

Welcome back to Reinforcement Learning. In our previous sessions, we’ve explored the fundamentals of learning through trial and error, focusing on how agents interact with their environments to achieve specific goals. We’ve examined basic algorithms like Q-learning, where an agent learns to estimate the optimal action-value function. Today, we’re building upon this understanding by introducing a formal framework for modeling these interactions: **Markov Decision Processes (MDPs)**. MDPs provide a rigorous mathematical foundation for understanding and designing reinforcement learning algorithms. Think of it this way: we've been implicitly dealing with MDPs all along, but now we're giving them a precise definition and a set of tools to analyze them. This framework allows us to translate a wide range of real-world problems—from robotics control to game playing—into a form that can be tackled by reinforcement learning techniques.

---

## Main Topic 1: Defining the Markov Decision Process

A **Markov Decision Process (MDP)** is a mathematical model used to represent decision-making problems where the outcome of an action is uncertain, and the future depends only on the current state and the action taken, not on the entire history of previous actions. It’s formally defined by a tuple of elements: S, A, P, R, and γ. Let’s break down each component:

*   **S**: The set of all possible **states**. A state represents the complete description of the environment at a particular point in time.  For instance, in a grid world game, each cell on the grid could represent a state. In a robotic navigation problem, the state might include the robot’s position and orientation.
*   **A**: The set of all possible **actions**. These are the choices the agent can make in each state.  For example, in a game of chess, each possible move constitutes an action.
*   **P**: The **transition probability distribution**. This specifies the probability of moving from one state to another after taking a specific action.  It’s represented as P(s’ | s, a), the probability of transitioning to state s’ after taking action ‘a’ in state ‘s’. This embodies the uncertainty inherent in real-world scenarios. Consider a self-driving car; the probability of reaching a safe intersection after braking (action) depends on road conditions (state).
*   **R**: The **reward function**. This defines the immediate reward the agent receives after taking an action in a state.  It’s often denoted as R(s, a), representing the reward received for taking action ‘a’ in state ‘s’. Rewards can be positive (encouraging an action) or negative (discouraging an action), or zero. For instance, in a video game, reaching a level might grant a positive reward, while taking damage might result in a negative reward.
*   **γ**: The **discount factor** (0 ≤ γ ≤ 1). This factor determines how much the agent values future rewards compared to immediate rewards. A γ close to 1 means the agent considers long-term rewards equally important as short-term rewards. A γ close to 0 indicates the agent is primarily concerned with immediate gratification. It essentially reflects the concept of temporal discounting – people often value something today more than the same thing in the future.

---

## Main Topic 2: Formalizing the Problem

The goal of reinforcement learning within an MDP is to learn an **optimal policy**. A policy, denoted as π, is a mapping from states to actions. It dictates what action the agent should take in each state.  We can represent this formally as π(s) = a, meaning that in state ‘s’, the agent should take action ‘a’.  The agent’s objective is to find the policy that maximizes the expected cumulative discounted reward, which is formally expressed as:

E[ Σ(γ<sup>t</sup> * R(s<sub>t</sub>, a<sub>t</sub>))]

Where:

*   E[ ] denotes the expected value
*   Σ(γ<sup>t</sup> * R(s<sub>t</sub>, a<sub>t</sub>)) represents the sum of discounted rewards over all time steps.
*   t represents the time step

This equation essentially says: "Take the expected value of the sum of all discounted rewards, where the discount factor (γ) reduces the importance of rewards received further in the future."

Consider a robot learning to walk. The state might include the robot's joint angles and velocities. Actions could include adjusting motor commands. The reward function might be based on distance traveled and maintaining balance. The agent learns a policy that minimizes falling and maximizes forward movement, considering the discounted value of future steps.

---

## Main Topic 3: Examples of MDPs

Let’s examine a few concrete examples to solidify our understanding:

1.  **Grid World**: As previously mentioned, this classic example involves an agent navigating a grid, avoiding obstacles, and reaching a goal state, receiving positive rewards for reaching the goal and negative rewards for hitting walls.
2.  **Inventory Management**: An agent controls inventory levels, ordering products based on demand, receiving rewards for meeting customer needs and penalties for overstocking or stockouts. The state might include current inventory levels, demand forecasts, and lead times.
3.  **Resource Allocation**: An agent decides how to allocate resources among different tasks, receiving rewards based on the overall efficiency and performance of the system.

---

## Main Topic 4: Bellman Equations – The Core of the Solution

The **Bellman equations** are a set of recursive equations that form the foundation for solving MDPs. They provide a way to calculate the optimal value function, which represents the expected discounted cumulative reward achievable from a given state. There are two main Bellman equations:

*   **Bellman Optimality Equation (Value Equation):** V<sup>π</sup>(s) = max<sub>a</sub> [ R(s, a) + γ * Σ(γ<sup>t+1</sup> * V<sup>π</sup>(s'))] This equation calculates the optimal value of a state ‘s’ under policy ‘π’. It states that the optimal value of a state is the maximum expected reward achievable by taking any action in that state, considering the expected discounted reward achievable from the next state.
*   **Bellman Equation for the Action-Value Function (Q-function):** Q<sup>π</sup>(s, a) = E[ Σ(γ<sup>t</sup> * R(s<sub>t</sub>, a<sub>t</sub>) + γ<sup>t+1</sup> * Q<sup>π</sup>(s<sub>t+1</sub>, a<sub>t+1</sub>))] This equation calculates the optimal action-value of taking action ‘a’ in state ‘s’ under policy ‘π’.

These equations are recursive, meaning that the value of a state depends on the values of its successor states. This recursive property allows us to systematically solve MDPs.

---

## Main Topic 5: Markov Property

A crucial aspect of MDPs is the **Markov property**. This states that the future state depends only on the current state and the action taken, and not on the entire history of the system.  In simpler terms, the “memory” of the past is irrelevant. This greatly simplifies the problem, as we only need to consider the current state and action to predict the future.  Without this assumption, the problem would be exponentially more complex.

Consider a stock trading system. The Markov property assumes that the price of a stock tomorrow depends only on its current price and today’s trading activity, not on past price fluctuations.

---

## Summary

Today’s session introduced the fundamental concepts of Markov Decision Processes – a powerful framework for modeling sequential decision-making problems. We defined the key components of an MDP: states, actions, transition probabilities, rewards, and the discount factor. We explored the Bellman equations, which provide a recursive method for solving MDPs, and emphasized the importance of the Markov property.  Crucially, we learned that MDPs form the theoretical foundation upon which many reinforcement learning algorithms are built.  Understanding MDPs is essential for designing and implementing effective reinforcement learning solutions. Next time, we’ll delve into specific algorithms, such as Value Iteration and Policy Iteration, that utilize these MDPs to learn optimal policies.