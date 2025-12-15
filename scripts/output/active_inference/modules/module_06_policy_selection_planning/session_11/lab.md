# Policy Selection & Planning - Laboratory Exercise 11

## Lab Focus: Policy Optimization

---

**Lab Number: 11**
**Lab Focus: Policy Optimization**

**1. Brief Background (98 words)**

This lab builds upon the principles of policy optimization introduced in the lecture. We will explore a simplified reinforcement learning scenario using a discrete state space. The core concept mirrors the lecture’s discussion of agent-environment interaction and reward maximization.  Similar to the exploration of Dynamic Programming, this lab focuses on iterative refinement. However, unlike deterministic methods, we'll utilize a simulated environment where the agent's actions directly influence the observed state, mimicking the predictive element central to Active Inference.  The goal is to develop an understanding of how different action choices impact the reward signal, allowing you to build a policy that maximizes cumulative reward.

**2. Lab Objectives (4 bullet points)**

*   Design a simple policy to navigate a simulated environment.
*   Collect data on state transitions and rewards for different action sequences.
*   Analyze the impact of distinct actions on the cumulative reward.
*   Develop an understanding of how reward functions shape policy development.

**3. Materials and Equipment**

*   **Software:** Python (version 3.8 or higher) with the following libraries: NumPy, Matplotlib
*   **Hardware:** Laptop with sufficient processing power (minimum 4GB RAM)
*   **Simulated Environment:** Custom Python script (provided by [INSTRUCTOR]) – simulates a simple maze with 5 states (A, B, C, D, E)
*   **Data Logging Tool:**  Spreadsheet software (Microsoft Excel, Google Sheets)
*   **Optional:** Graph paper for sketching maze layouts.

**4. Safety Considerations (⚠️)**

*   **Potential Hazards:** No specific chemical or biological hazards are present in this lab.  However, prolonged use of a laptop may contribute to eye strain.
*   **PPE Requirements:** Safety glasses must be worn at all times during the lab.  Ensure a stable workstation and sufficient lighting to minimize visual strain.
*   **Time-Sensitive Step:**  Do not execute the Python script repeatedly without observing the simulated environment state between runs.  This prevents confusion between different environment states.
*   **Emergency Stop:** [INSTRUCTOR] will implement a hard stop function in the simulation script that can be triggered immediately by [INSTRUCTOR] if needed.

**5. Procedure (7 steps)**

1.  **Set up the Simulation:**  Run the provided Python script to initialize the simulated maze environment. Verify that the states (A, B, C, D, E) are displayed correctly within the console output.
2.  **Define Actions:**  The agent can take two actions: “Move Left” or “Move Right”. Record each action in a separate column of your chosen data logging tool.
3.  **Execute Action Sequences:** Starting from state ‘A’ (the starting point), execute the following action sequences: (1) “Move Right”, “Move Right”, “Move Right”, “Move Right”. Record the final state and the received reward after each move.
4.  **Repeat:** Repeat step 3, executing a different action sequence – e.g., "Move Left", "Move Right", "Move Left".
5.  **Vary Sequences:**  Repeat steps 3-5, systematically exploring other action sequences within the environment.  Document all sequences attempted.
6. **Record Data:**  Carefully record the state transition and reward value for each action sequence in the provided data logging tool.
7. **Repeat:** Execute the entire procedure for a minimum of 3 different, randomly generated action sequences.

**6. Data Collection (Template)**

| Action Sequence | Initial State | State After Move 1 | Reward | Final State |
|------------------|---------------|--------------------|--------|-------------|
| (Sequence 1)     | A             |                    |        |             |
| (Sequence 2)     | A             |                    |        |             |
| (Sequence 3)     | A             |                    |        |             |
| ...               | ...           | ...                |        | ...         |

**7. Analysis Questions (5 questions)**

1.  How did the reward value change with each action? Explain the relationship between actions and reward.
2.  Which action sequences consistently led to higher cumulative rewards? Why do you think this was the case?
3.  If the reward function was altered (e.g., a negative reward for returning to state ‘A’), how would your policy need to change?
4.  How does this lab demonstrate the core concept of reinforcement learning – the agent’s attempt to maximize a cumulative reward?
5.  Explain how this lab relates to the concept of Active Inference, specifically the agent’s attempt to predict the outcome of its actions.

**8. Expected Results (2 paragraphs)**

Students should observe that certain action sequences consistently lead to higher cumulative rewards.  This is because the action choices directly impact the state transition, influencing the immediate reward and ultimately the overall reward trajectory. For example, a sequence of actions that leads the agent to a state with a higher reward value, or a state closer to the goal state, will generate a greater cumulative reward. Students should be able to correlate these observations with the reward function, recognizing that the agent is actively learning to associate specific actions with desirable outcomes.  Variations in the action sequence will clearly demonstrate the influence of action choices on the reward signal.