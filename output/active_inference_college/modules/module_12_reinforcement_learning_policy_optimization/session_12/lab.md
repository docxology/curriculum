# Reinforcement Learning – Policy Optimization - Laboratory Exercise 12

## Lab Focus: Transition Probabilities

---

**Module: Reinforcement Learning – Policy Optimization**
**Lab Number: 12**
**Lab Focus: Transition Probabilities**

**1. Brief Background (98 words)**

This lab builds upon our introduction to Markov Decision Processes (MDPs), formally defined as a tuple of S, A, P, R, and γ.  We’ve established the core concept of an agent interacting with an environment to maximize reward. This lab’s primary focus is on understanding how the *transition probabilities* (P) within an MDP dictate the agent’s learning process. We’ll explore how knowing the likelihood of moving from one state to another directly influences the agent’s ability to determine optimal policies. By manipulating these probabilities, we will illustrate the impact on learning and policy optimization. [INSTRUCTOR: Briefly demonstrate a simple grid world example on the board].

**2. Lab Objectives (4 bullet points)**

*   Identify the states, actions, and transition probabilities for a given simple MDP.
*   Modify the transition probabilities of an MDP and observe the impact on the agent’s behavior.
*   Determine the effect of a change in transition probabilities on the rate of learning.
*   Develop an understanding of how the ‘P’ component of the MDP definition influences the learning process.

**3. Materials and Equipment**

*   **Software:** Python 3.9+ with NumPy and Matplotlib libraries installed.
*   **Hardware:** Laptop computer with sufficient processing power.
*   **Components:**
    *   Grid World Environment (simulated in Python – see code example below)
    *   Transition Probability Modification Script (Python)
    *   Visualization Script (Python – Matplotlib)
    *   Transition Probability Table Template (printed)

**4. Safety Considerations (⚠️)**

*   **Electrical Safety:** Ensure all equipment is plugged into properly grounded outlets.  Do not operate equipment with damaged cords.
*   **Computer Strain:** Take regular breaks (every 60 minutes) to avoid eye strain and fatigue. Maintain a comfortable workspace.
*   **Data Security:**  Do not share your code or simulation data with unauthorized individuals. [INSTRUCTOR: Remind students about responsible data handling].

**5. Procedure (7 steps)**

1.  **Setup Environment:**  Run the provided Python script to initialize the simulated grid world environment. The script will display the grid.
2.  **Define Initial Transition Probabilities:** The script starts with a pre-defined set of transition probabilities for each cell in the grid. Record these initial values in the Transition Probability Table Template.
3.  **Run Simulation:** Execute the simulation for 100 steps. Observe the agent's movement based on the initial transition probabilities.
4.  **Modify Transition Probabilities:** Using the provided Python script, change the transition probability for cell (2, 2) from 0.3 to 0.7. Save the modified script.
5.  **Run Simulation (Modified):** Execute the simulation for 100 steps with the modified transition probabilities.
6.  **Data Collection:** Record the agent’s final position and the number of steps taken in the table below. Repeat steps 5 and 6 at least three times to gather multiple data points.
7.  **Repeat:** Repeat steps 5-7, this time changing the transition probability for cell (1, 1) from 0.5 to 0.8.

**6. Data Collection**

| Trial | Final Position (x, y) | Number of Steps | Initial Transition Probabilities (Example) | Modified Transition Probabilities (Example) |
|-------|-----------------------|-----------------|-------------------------------------------|------------------------------------------|
| 1     |                       |                 | P((2,2))=0.3, P((1,1))=0.5               | P((2,2))=0.7, P((1,1))=0.5               |
| 2     |                       |                 |                                           |                                          |
| 3     |                       |                 |                                           |                                          |
| 4     |                       |                 |                                           |                                          |

**7. Analysis Questions (5 questions)**

1.  How did the change in transition probabilities for cell (2, 2) affect the agent’s path to the goal? Explain.
2.  In what ways did the altered probabilities impact the number of steps the agent took to reach the goal?
3.  If the transition probability from (1,1) to (2,2) was increased to 0.9, what might you observe differently?
4.  How does this lab exercise illustrate the importance of the transition probability matrix (P) within an MDP?
5.  Consider a more complex MDP (e.g., a maze). How would the approach of modifying transition probabilities apply?

**8. Expected Results (2 sentences)**

Students should observe that altering transition probabilities significantly influences the agent’s learning and pathfinding behavior. They will likely see the agent converge to the goal more quickly when transition probabilities are favorable and explore different paths if the transition probabilities are designed to mislead.  [INSTRUCTOR: Guide students to connect the modifications to changes in Q-value updates.]