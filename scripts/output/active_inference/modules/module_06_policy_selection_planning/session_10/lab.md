# Policy Selection & Planning - Laboratory Exercise 10

## Lab Focus: Cost Functions

---

**Module: Policy Selection & Planning – Lab 10: Cost Functions**

**Lab Number:** 10
**Lab Focus:** Cost Functions

**1. Brief Background (87 words)**

This laboratory exercise builds upon the principles of optimal control theory introduced in Lecture 10. We’ll explore the fundamental role of the Hamiltonian and cost functions in designing control policies. The core concept is translating the problem of finding the ‘best’ control strategy into a calculus problem. Students will manipulate a simplified system to understand how changes in the cost function directly impact the optimal control strategy. This exercise emphasizes the direct link between mathematical formulation and practical control design.

**2. Lab Objectives (4 bullet points)**

*   Calculate the Hamiltonian for a given system dynamics.
*   Determine the optimal control law using the Pontryagin's Minimum Principle.
*   Analyze the impact of varying the cost function on the resulting optimal control.
*   Implement and interpret the results of a simplified optimal control simulation.

**3. Materials and Equipment**

*   **Hardware:**
    *   LabQuest 2 Data Acquisition System (1 per group)
    *   DC Motor (12V, 100 RPM)
    *   Small Block (approximately 5cm x 5cm x 3cm)
    *   Pulley and String
    *   Linear Track (1 meter length)
    *   Power Supply (12V DC)
*   **Software:**
    *   LabQuest Data Acquisition Software (Version 3.1 or later)
    *   Spreadsheet Software (e.g., Microsoft Excel, Google Sheets)
*   **Consumables:**
    *   Connecting Wire
    *   Tape
    *   Ruler (metric)

**4. Safety Considerations (⚠️)**

⚠️ **Potential Hazards:**
*   **Electrical Shock:**  Handle power supplies and connecting wires with care. Avoid contact with exposed wires. Ensure power supply is properly grounded.
*   **Mechanical Hazards:**  The DC motor can rotate at high speeds. Maintain a safe distance between hands and moving parts. ⚠️
*   **Trip Hazard:** Ensure the linear track is securely positioned to prevent tripping.

PPE Requirements:
*   Safety Goggles (ANSI Z87.1 certified) - *Mandatory*
*   Lab Coat – *Recommended*

**5. Procedure (7 steps)**

1.  **Setup:** Securely mount the linear track on a stable surface. Attach the DC motor to the end of the track using the pulley and string. Ensure the block can freely move along the track.
2.  **Calibration:** Using the LabQuest 2, set up the data acquisition system to record the motor’s speed (RPM) as a function of time.
3.  **Initial Conditions:** Set the motor speed to 60 RPM and record this value for 60 seconds. This will be your initial condition *x(0)*.
4.  **Cost Function Introduction:** [INSTRUCTOR] – Introduce the Hamiltonian function *H(x, ẋ, t) = ẋ² + kx*, where *k = 0.5 Ns²* (This value will be discussed in more detail). This represents a cost function that penalizes both velocity (ẋ) and position (x).
5.  **Control Manipulation:**  [INSTRUCTOR] – Instruct students to gradually increase the value of *k* in the Hamiltonian function. Observe the motor's behavior and record the resulting speed.  Repeat for *k* values of 1, 2, and 3 Ns².
6.  **Data Recording:** For each *k* value, record the motor speed (RPM) and the corresponding time (60 seconds).
7.  **Repeat:** Repeat steps 5 and 6 for a total of 60 seconds of data collection.

**6. Data Collection**

| Time (s) | Motor Speed (RPM) | k (Ns²) |
|---|---|---|
| 0 | 60 | 0.5 |
| 10 |  | 1 |
| 20 |  | 2 |
| 30 |  | 3 |
| 40 |  |  |
| 50 |  |  |
| 60 |  |  |

*Note: Record all data points collected during the experiment.*

**7. Analysis Questions (5 bullet points)**

*   How did increasing the value of *k* affect the motor’s speed? Explain the relationship between the cost function and the control action.
*   Describe the optimal control strategy that resulted from minimizing the Hamiltonian.  How does it compare to simply maintaining a constant speed?
*   If the cost function were different (e.g., *H(x, ẋ, t) = ẋ² + αx*), what would be the impact on the optimal control?
*   Explain why minimizing the Hamiltonian leads to the optimal control strategy. Connect this to the concept of Pontryagin’s Minimum Principle.
*   Consider a scenario where the block needs to move to a specific destination.  How would you modify the Hamiltonian to incorporate this constraint?

**8. Expected Results (2 paragraphs)**

Students should observe that as the value of *k* increases, the motor’s speed decreases. This is because the cost function penalizes both velocity and position, leading to a more conservative control strategy. The optimal control will be a decrease in motor speed to minimize the total cost.  The data collected should demonstrate a clear correlation between the cost function parameter (*k*) and the resulting optimal motor speed. A visually appealing plot of motor speed vs. time, alongside the changes in *k*, will clearly demonstrate the influence of the cost function on the system’s behavior.  [INSTRUCTOR] – Emphasize the importance of understanding how cost functions influence control policy design.