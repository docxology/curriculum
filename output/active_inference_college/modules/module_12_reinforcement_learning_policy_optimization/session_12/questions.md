# Reinforcement Learning – Policy Optimization - Comprehension Questions

**Total Questions**: 10  
**Multiple Choice**: 5 | **Short Answer**: 3 | **Essay**: 2

---

**Question 1:** What is the primary function of mitochondria?
A) Protein synthesis
B) ATP production
C) DNA storage
D) Waste removal
**Answer:** B
**Explanation:** Mitochondria are the powerhouses of the cell, producing ATP through cellular respiration. They contain the electron transport chain and ATP synthase complexes that generate energy from glucose breakdown.

**Question 2:** Which of the following best describes the concept of a Markov Decision Process (MDP)?
A) A model that predicts future events with certainty.
B) A mathematical framework for modeling sequential decision-making problems.
C) A method for optimizing complex algorithms in real-time.
D) A technique for creating detailed simulations of physical systems.
**Answer:** B
**Explanation:** An MDP provides a formal structure for representing decision-making scenarios where outcomes depend on the current state and action, not the entire history. It's a core concept in reinforcement learning.

**Question 3:** In the context of an MDP, what does the ‘P’ component represent?
A) The total reward received by the agent.
B) The set of possible states in the environment.
C) The transition probabilities between states.
D) The discount factor used in the reward calculation.
**Answer:** C
**Explanation:** ‘P’ denotes the probabilities of transitioning from one state to another after taking a specific action – a crucial element for modeling the environment’s dynamics.

**Question 4:**  What is a key difference between a prokaryotic cell and a eukaryotic cell?
A) Prokaryotic cells are larger and more complex.
B) Eukaryotic cells contain a nucleus, while prokaryotic cells do not.
C) Prokaryotic cells perform photosynthesis, while eukaryotic cells do not.
D) Eukaryotic cells have membrane-bound organelles, whereas prokaryotic cells do not.
**Answer:** D
**Explanation:** Eukaryotic cells possess internal compartmentalization through membrane-bound organelles, significantly enhancing their complexity and functional capabilities compared to the simpler prokaryotic cell structure.

**Question 5:** What is the purpose of a discount factor (γ) in reinforcement learning?
A) To increase the immediate reward received by the agent.
B) To decrease the importance of future rewards relative to immediate rewards.
C) To directly influence the agent’s exploration strategy.
D) To limit the total number of steps the agent can take.
**Answer:** B
**Explanation:** The discount factor, gamma (γ), determines how much the agent values future rewards compared to immediate ones, impacting the learning process and policy optimization.

**Question 6:**  Describe the role of transition probabilities (P) in an MDP.?
**Answer:** Transition probabilities (P) define the likelihood of moving from one state to another when a specific action is taken. These probabilities dictate the dynamics of the environment and are essential for the agent to learn an optimal policy.  Changes to P directly impact the agent's learning trajectory.

**Question 7:** Explain how modifying transition probabilities could affect an agent's learning process in an MDP.?
**Answer:** Altering transition probabilities directly influences the agent's ability to estimate optimal actions. If transitions become more predictable, the agent can quickly converge to a policy. Conversely, if transitions become more random or less informative, learning will be slower and more challenging.

**Question 8:**  Discuss a potential real-world application of MDPs in robotics.?
**Answer:** MDPs are frequently used in robotics for navigation tasks.  An agent controlling a robot in a complex environment (like a warehouse or a building) can utilize an MDP to learn the optimal path to reach a goal, considering obstacles and varying terrain. The state could include the robot’s location and orientation, while actions could represent movement commands.

**Question 9:**  Explain how understanding the concept of Markov Property contributes to the usefulness of MDPs.?
**Answer:** The Markov Property – the assumption that the future state depends only on the present state and action, not the past – is crucial because it simplifies the problem.  It allows us to focus solely on the current situation and make informed decisions, avoiding the need to track an endless chain of past events, thereby making analysis and algorithm design more tractable.

**Question 10:**  Summarize the key components of an MDP and explain how they are interconnected.?
**Answer:** An MDP consists of S (states), A (actions), P (transition probabilities), R (rewards), and γ (discount factor). These elements are interconnected: Actions determine state transitions (P), which then influence the reward received, and the discount factor shapes the agent's evaluation of future rewards, ultimately guiding its learning towards an optimal policy.