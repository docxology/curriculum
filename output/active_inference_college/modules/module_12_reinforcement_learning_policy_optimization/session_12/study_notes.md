# Reinforcement Learning – Policy Optimization - Study Notes

## Key Concepts

## Reinforcement Learning – Policy Optimization: Study Notes

**Introduction:**

This module focuses on the foundational concept of Policy Optimization within Reinforcement Learning. We’ll build upon our understanding of Markov Decision Processes (MDPs) to explore how agents learn optimal actions through trial and error. The core of this module is understanding and manipulating the policy – the strategy an agent uses to select actions.

**Key Concepts:**

**Policy**: Policy: A policy is a strategy or rule that an agent follows to determine which action to take in a given state. It can be deterministic (mapping each state to a single action) or stochastic (assigning a probability distribution over actions). Think of it as the agent's "brain" – the way it decides what to do.

**Markov Decision Process (MDP)**: MDP: A mathematical framework used to model decision-making problems with uncertainty. It consists of four key elements: states, actions, transition probabilities, and rewards. It’s the foundation upon which we build reinforcement learning algorithms.

**State**: State:  A state represents the complete description of the environment at a particular moment in time.  It’s the agent’s perception of the world.  Examples include a robot’s position and orientation, a game board configuration, or a sensor reading.

**Action**: Action: An action is a choice the agent makes within a given state. The set of all possible actions available to the agent in a state is called the action space.

**Transition Probability**: Transition Probability: The probability of moving from one state to another after taking a specific action.  This represents the uncertainty inherent in the environment.  It’s often denoted as P(s’ | s, a), meaning the probability of transitioning to state ‘s’ given that the agent is currently in state ‘s’ and takes action ‘a’.

**Reward**: Reward: A scalar value that the agent receives after taking an action in a state. Rewards signal to the agent whether an action was desirable or undesirable. Positive rewards reinforce good behavior, while negative rewards (penalties) discourage bad behavior.

**Value Function**: Value Function: A function that estimates the expected cumulative reward an agent will receive starting from a particular state and following a specific policy. There are two main types: State-Value Function (V(s)) and Action-Value Function (Q(s, a)).

**Q-Value**: Q-Value: The Q-Value (Q(s, a)) represents the expected cumulative reward for taking action ‘a’ in state ‘s’ and then following the optimal policy thereafter. It's a key element in algorithms like Q-learning.

**Policy Iteration**: Policy Iteration: An iterative algorithm used to find the optimal policy for an MDP. It involves repeatedly evaluating the value function for the current policy and updating the policy based on this value function.

**Value Iteration**: Value Iteration: An alternative iterative algorithm for finding the optimal policy. Unlike Policy Iteration, it directly updates the value function at each step.

**Mnemonics/Memory Aids:**

*   **V(s):** “Value of State” – Remember this is the expected reward from a state.
*   **Q(s, a):** “Quality of a State-Action Pair” – Helps recall the Q-Value.