# Markov Models – Introduction & State Spaces - Laboratory Exercise 7

## Lab Focus: State Transitions

---

**Module: Markov Models – Introduction & State Spaces**
**Lab Number: 7**
**Lab Focus: State Transitions**

**1. Brief Background (87 words)**

This laboratory exercise builds upon our discussion of Markov models and the Markov Property – the core principle that the future state of a system depends solely on the present state. You’ll be exploring state transitions within a simplified system. By systematically observing how states change based on current conditions, you'll gain a concrete understanding of how transition probabilities govern a Markov model.  The goal is to directly apply the concept of memorylessness, demonstrating how a model can accurately predict future states given only the present state.

**2. Lab Objectives (4 bullet points)**

*   Observe and record state transitions in a simulated system.
*   Calculate transition probabilities based on observed state changes.
*   Construct a simple transition matrix representing the system’s behavior.
*   Analyze the impact of varying initial states on subsequent transitions.
*   Evaluate the accuracy of the model’s predictions based on observed data.

**3. Materials and Equipment**

*   **System:**  Wooden Gear Set (12 gears, various sizes – 3cm, 5cm, 7cm, 9cm, 12cm)
*   **Tracking Tools:**  Colored Markers (Red, Blue, Green) - 10 each
*   **Measurement Tools:** Ruler (cm scale, 10cm increments), Stopwatch
*   **Data Recording:** Whiteboards (3), Whiteboard Markers (Black)
*   **Data Sheets:** Printed Data Collection Tables (see Section 6)
*   **Surface:**  Hardwood Table

**4. Safety Considerations (⚠️)**

⚠️ **Physical Hazard:**  The gears can be dropped and cause minor bruising. Exercise caution to avoid collisions.
⚠️ **Eye Protection:**  Safety goggles *must* be worn at all times during the experiment.
⚠️ **Cleanliness:**  Clean up any dropped gears immediately.
⚠️ **Time-Sensitive Step (15 seconds):**  Rapid movement of gears creates a potential tripping hazard. Maintain a clear working space.
*PPE Requirements:* Safety Goggles, Closed-toe shoes.

**5. Procedure (7 steps)**

1.  **Setup:** Arrange the wooden gears on the hardwood table. Ensure adequate space between gears to allow for rotation.
2.  **Initial State:**  Begin with all gears in a fixed, starting configuration (e.g., all gears aligned so that gear 1 is at 0 degrees). Mark this initial state on the whiteboard with a red marker.
3.  **Transition Step 1 (10 seconds):** Rotate gear 1 clockwise by 30 degrees. Immediately mark the new state with a blue marker on the whiteboard.
4.  **Transition Step 2 (10 seconds):** Rotate gear 1 clockwise by 30 degrees. Immediately mark the new state with a blue marker on the whiteboard.
5.  **Repeat Steps 3 & 4:** Continue rotating gear 1 clockwise by 30 degrees a total of 5 times (30 degrees x 5 rotations = 150 degrees).  Record each state transition using a blue marker.
6.  **State Analysis:**  Observe the final state of the gear system.  Identify the number of times each initial gear configuration appeared in the sequence of transitions.
7.  **Repeat:** Repeat steps 1-7 a minimum of 3 times.

**6. Data Collection**

| Trial | Initial State (Degrees) | Final State (Degrees) | Transition |
|---|---|---|---|
| 1 | 0 |  |  |
| 1 |  |  |  |
| 2 | 0 |  |  |
| 2 |  |  |  |
| 3 | 0 |  |  |
| 3 |  |  |  |
| ... | ... | ... | ... |

*(Students will record the state after each transition in this table)*

**7. Analysis Questions**

1.  Define the state space of this system. What are the possible states?
2.  Construct a transition matrix representing the system's behavior, based on your observed transitions.
3.  If the initial state was always '0', what would you expect the final state to be after 150 degrees of rotation?  Explain your reasoning.
4.  How does the Markov Property apply to this system?  Consider the influence of the initial state on subsequent state changes.
5. How does the number of transitions affect the data collected?

**8. Expected Results**

Students should observe that after 150 degrees of rotation of Gear 1, the gear system will return to the initial configuration (0 degrees).  This demonstrates a cyclical behavior and illustrates the concept of a Markov chain. The transition matrix will show probabilities corresponding to returning to the initial state. The number of transitions influences the data collected: a longer period of observation would theoretically increase the likelihood of returning to the initial state.