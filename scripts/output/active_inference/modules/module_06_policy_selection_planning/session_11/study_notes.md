# Policy Selection & Planning - Study Notes

## Key Concepts

## Policy Selection & Planning: Core Concepts

This document outlines key concepts for understanding Policy Selection & Planning, drawing heavily from Reinforcement Learning and Active Inference principles.

**Concept Name**: Reinforcement Learning (RL): A framework where an agent learns to make decisions within an environment to maximize a cumulative reward. The agent interacts with the environment, observing states, taking actions, and receiving feedback (rewards or penalties). It then adjusts its strategy (policy) based on this feedback.

**Concept Name**: Temporal Difference Learning: A type of RL where the agent learns by predicting the value of a state based on the difference between predicted and observed rewards. This is achieved by bootstrapping – using previous estimates to update current estimates.  Essentially, it's learning "from experience" by comparing what *should* happen with an action to what *actually* happened.

**Concept Name**: Reward Functions: Mathematical expressions that quantify the desirability of a state or action.  They are the cornerstone of RL, guiding the agent’s learning process by indicating what constitutes “good” behavior.  A well-designed reward function is crucial for successful learning.

**Concept Name**: Value Functions:  Represent the expected cumulative reward an agent can achieve starting from a particular state and following a specific policy. There are two main types: State-Value Function (V(s)) and Action-Value Function (Q(s,a)).

**Concept Name**: Policy: A strategy that dictates which action an agent should take in a given state.  It can be deterministic (mapping directly from states to actions) or stochastic (specifying a probability distribution over actions).

**Concept Name**: State: A specific configuration of the environment at a particular point in time. It contains all the information necessary to make a decision. In a navigation scenario, this could include the robot's location, the position of obstacles, and the goal location.

**Concept Name**: Active Inference: A theoretical framework that posits agents learn by predicting their own sensory consequences. Instead of passively receiving information from the environment, the agent actively *models* the world and uses this model to anticipate what will happen if it takes a certain action. This predictive element is vital for learning and decision-making.

**Concept Name**: Dynamic Programming: An algorithmic approach to solving sequential decision problems. It breaks down a complex problem into smaller, overlapping subproblems, solving each subproblem once and storing the solution for later use. It often relies on the concept of a value function to guide the optimization process.

**Concept Name**: Value Iteration: An iterative algorithm used in dynamic programming to find the optimal value function. It repeatedly updates the value of each state until the value function converges to its optimal value.

**Memory Aid**: Think of ‘Active Inference’ as “Actively Anticipating Consequences” – a helpful mnemonic for remembering the core principle.