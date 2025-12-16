# Predictive Coding – Neural Basis - Laboratory Exercise 10

## Lab Focus: Hierarchical Predictions

---

**Module: Predictive Coding – Neural Basis**
**Lab Number: 10**
**Lab Focus: Hierarchical Predictions**

**1. Brief Background (87 words)**

This laboratory exercise builds upon the concepts presented in today’s lecture concerning the Encoder-Decoder model and hierarchical predictions. We will simulate aspects of this model using a simple, dynamic system – a double pendulum. The double pendulum demonstrates hierarchical prediction; lower-level motion influences higher-level predictions, mirroring the brain’s ability to generate and refine internal models of the external world. By manipulating the system, students will observe how changes in initial conditions and parameters directly impact the predicted output, highlighting the iterative nature of the predictive coding loop.

**2. Lab Objectives (4 bullet points)**

*   Construct a double pendulum system and demonstrate its oscillatory behavior.
*   Modify the initial conditions of the pendulum and observe the resulting changes in its motion.
*   Record and analyze the system's behavior over time, identifying periods of sustained motion and periods of damped oscillation.
*   Compare and contrast the system’s behavior with and without a predetermined initial trajectory, illustrating predictive error.

**3. Materials and Equipment**

*   **Mechanical:**
    *   Double Pendulum Kit (including two steel balls, two rods – approximately 30cm long, with threaded connections) – Quantity: 1 set
    *   Small weights (e.g., 50g metal washers) – Quantity: 10
    *   Thread (approximately 1m length, 3mm diameter) - Quantity: 2 meters
*   **Measurement & Observation:**
    *   Stopwatch – Quantity: 1
    *   Measuring Tape – Quantity: 1
    *   Whiteboard or Large Paper – Quantity: 1
    *   Markers – Quantity: 5 (various colors)
*   **Computer:** Computer with spreadsheet software (e.g., Microsoft Excel)

**4. Safety Considerations (⚠️)**

*   ⚠️ **Physical Hazard:**  The pendulum can swing forcefully. Maintain a safe distance (minimum 1 meter) from the swinging pendulum at all times. [INSTRUCTOR] – Monitor student positioning.
*   ⚠️ **Trip Hazard:**  Ensure the lab bench is clear of obstructions.
*   ⚠️ **Glassware:** The pendulum kit may include small screw connections - avoid striking these forcefully.
*   PPE: Safety goggles are *required* at all times during the experiment.  [INSTRUCTOR] – Ensure all students are wearing appropriate PPE.

**5. Procedure (7 steps)**

1.  Assemble the double pendulum according to the kit’s instructions.  Ensure all connections are secure.
2.  With no initial force applied, allow the pendulum to oscillate freely for 60 seconds. Record the observed pattern of motion on the whiteboard, noting any identifiable features (e.g., period, amplitude, symmetry).
3.  Using the stopwatch, initiate the pendulum with a single, sharp push.  Measure and record the initial velocity imparted (e.g., 5cm/s).
4.  Observe the pendulum’s behavior over 90 seconds, noting any changes in its motion. Record observations on the whiteboard.
5.  Repeat steps 3 & 4 five times, varying the initial velocity (e.g., 3cm/s, 7cm/s, 10cm/s).  Record each velocity and the corresponding observed motion.
6.  Calculate the average amplitude of oscillation for each initial velocity.
7.  Repeat steps 3-6 three times with no initial push.

**6. Data Collection**

| Initial Velocity (cm/s) | Trial 1 Amplitude (cm) | Trial 2 Amplitude (cm) | Trial 3 Amplitude (cm) | Average Amplitude (cm) |
| :----------------------- | :-------------------- | :-------------------- | :-------------------- | :-------------------- |
| 5                        |                       |                       |                       |                       |
| 3                        |                       |                       |                       |                       |
| 7                        |                       |                       |                       |                       |
| 10                       |                       |                       |                       |                       |
| 0 (No Initial Push)        |                       |                       |                       |                       |

**7. Analysis Questions (5 questions)**

1.  How did the initial velocity of the pendulum influence its behavior?  Describe the relationship between the applied force and the system’s output.
2.  In what ways did the system’s motion change when no initial force was applied?  What does this suggest about the system's internal state?
3.  Consider the double pendulum as a neural system. What does the “error signal” represent in this context?
4.  How does the observed behavior of the double pendulum relate to the concept of hierarchical prediction?
5.  If the pendulum were to exhibit chaotic behavior, what might be the implications for the Encoder-Decoder model and the brain's ability to generate accurate predictions?

**8. Expected Results (2 paragraphs)**

Students should observe that a larger initial velocity results in a larger amplitude of oscillation, indicating a greater initial perturbation of the system's internal state.  Without an initial push, the pendulum will eventually settle into a repeating, damped oscillation. This behavior demonstrates the system's inherent tendency to minimize its error – returning to a stable state after a disturbance.  Furthermore, students should see a clear impact of the initial conditions, highlighting the system's sensitivity to initial states, a key aspect of chaotic systems and how this relates to predictive coding. [INSTRUCTOR] –  Guide student discussion about the relationship between the initial conditions and the observed oscillations.