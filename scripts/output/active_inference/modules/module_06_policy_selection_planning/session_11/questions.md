# Policy Selection & Planning - Comprehension Questions

**Total Questions**: 10  
**Multiple Choice**: 5 | **Short Answer**: 3 | **Essay**: 2

---

**Question 1:** Which of the following best describes the core principle of reinforcement learning?
A) Predicting future events with certainty
B) Maximizing immediate rewards without considering long-term consequences
C) Learning through trial and error, adjusting actions based on received rewards
D) Maintaining a static policy regardless of environmental changes?
**Answer:** C
**Explanation:** Reinforcement learning centers on an agent learning to optimize a policy by repeatedly interacting with an environment, receiving rewards or penalties based on its actions, and adjusting its strategy to maximize cumulative reward over time.

**Question 2:** What is the primary function of a reward function in reinforcement learning?
A) To directly control the agent’s actions
B) To provide feedback to the agent indicating the desirability of its actions
C) To define the state of the environment
D) To prevent the agent from exploring the environment?
**Answer:** B
**Explanation:** A reward function assigns a numerical value to outcomes, guiding the agent to learn actions that lead to higher rewards.  This feedback is crucial for the agent’s learning process within the reinforcement learning framework.

**Question 3:**  In the context of Active Inference, how does a robot’s movement relate to sensory predictions?
A) Robots passively receive sensory input and react accordingly
B) Robots generate random movements to explore the environment
C) Robots predict the sensory consequences of their movements and adjust actions to match those predictions
D) Robots solely respond to external stimuli without any predictive processing?
**Answer:** C
**Explanation:** Active Inference posits that agents actively predict their sensory consequences, using these predictions to guide their actions and adapt to the environment, a key element in how RL agents learn.

**Question 4:** What distinguishes a dynamic programming approach from other methods of policy optimization?
A) It relies solely on random exploration
B) It involves directly calculating the optimal policy through value iteration
C) It requires a detailed understanding of the environment’s transition probabilities
D) It's primarily used for solving problems with discrete state spaces only?
**Answer:** B
**Explanation:** Dynamic programming utilizes iterative value calculations to determine the optimal policy, systematically refining the agent's actions based on estimated future rewards in a deterministic environment.

**Question 5:**  What role does the environment play in reinforcement learning?
A) The environment is static and unchanging
B) The environment passively receives the agent's actions
C) The environment provides feedback (rewards/penalties) to the agent’s actions
D) The environment only exists to provide initial state information?
**Answer:** C
**Explanation:** The environment is the system the agent interacts with.  It’s crucial because it determines the reward signal, directly influencing the learning process and shaping the agent's policy.

**Question 6:** Explain the concept of a "state" in reinforcement learning?
**Answer:** In reinforcement learning, a state represents a specific configuration of the environment at a given point in time. It encompasses all the relevant information the agent needs to make a decision. This could include the agent's position, the current configuration of objects in the environment, or any other factors impacting its situation.

**Question 7:**  Describe how the concept of "trial and error" relates to reinforcement learning.?
**Answer:**  Reinforcement learning fundamentally relies on trial and error. The agent explores different actions within the environment, observing the resulting rewards or penalties.  Through this iterative process, it gradually learns which actions lead to the most desirable outcomes, improving its policy over time.

**Question 8:**  How might a reward function be designed to encourage a robot to navigate a maze efficiently?
**Answer:** A reward function could be designed to award positive rewards for reaching the goal state and negative rewards for collisions or long paths.  The magnitude of these rewards would influence the agent’s exploration strategy and ultimately, the efficiency of its navigation policy.

**Question 9:**  Explain how the principle of maximizing cumulative reward relates to the overall goal of reinforcement learning?
**Answer:** The central objective of reinforcement learning is to maximize the agent's cumulative reward over time. This means the agent strives to take actions that not only produce immediate rewards but also contribute to a greater, long-term reward signal.

**Question 10:**  In what ways does the concept of "exploration" relate to reinforcement learning?
**Answer:** Exploration is critical in reinforcement learning. It involves the agent venturing into unfamiliar parts of the environment to discover new actions and potential rewards. This contrasts with exploitation, where the agent sticks to actions known to yield rewards.