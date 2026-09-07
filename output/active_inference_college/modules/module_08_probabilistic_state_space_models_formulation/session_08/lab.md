# Probabilistic State-Space Models – Formulation - Laboratory Exercise 8

## Lab Focus: Sensory Input

---

**Module: Probabilistic State-Space Models – Formulation**
**Lab Number: 8**
**Lab Focus: Sensory Input**

**1. Brief Background (98 words)**

Following our lecture on the formulation of probabilistic state-space models, this lab focuses on translating the core state equation – *x<sub>t+1</sub> = f(x<sub>t</sub>, u<sub>t</sub>, w<sub>t</sub>)* – into a practical, simulated environment. We will use a simplified model of a robot navigating a 1D linear track. The robot's state will be its position along the track, and its movement will be governed by a noisy input, mimicking a sensor providing limited information. This exercise will reinforce the understanding of how the state evolves based on both internal dynamics (the ‘f’ function) and external influences (sensor input, noise). [INSTRUCTOR: Briefly demonstrate the simulated environment.]

**2. Lab Objectives (4 bullet points)**

*   Simulate a robot’s movement along a linear track.
*   Implement a simple state equation using provided code.
*   Analyze the impact of a noisy input on the robot's position.
*   Record and interpret data related to the robot’s state.

**3. Materials and Equipment**

*   **Computer:**  Laptop or desktop with MATLAB (R2023 or later) installed.
*   **Software:** MATLAB, with the following script (provided by [INSTRUCTOR] – this script simulates the robot’s movement and noisy sensor input):
    ```matlab
    % Robot Simulation Parameters
    dt = 0.1; % Time step
    track_length = 10; % Length of the track
    noise_std = 0.5; % Standard deviation of the noise

    % Initialize Robot State
    x = 0; % Initial position
    u = 0; % Control Input (Step Size)
    t = 0;

    % Simulation Loop
    for t = 1:100
        % State Equation Implementation (Simplified)
        x_next = x + u * dt;
        w = noise_std * randn(); % Generate Noise
        x = x_next + w;

        % Ensure Robot Stays Within Track Boundaries
        x = max(0, min(x, track_length));

        % Display Current State
        disp(['Time: ', num2str(t), ', Position: ', num2str(x)]);
        t = t + dt;
    end
    ```
*   Calibration Tools: Ruler (for reference only, not for actual measurement).

**4. Safety Considerations (⚠️)**

*   **No Chemical Hazards:** This lab involves solely software simulation – no hazardous materials are present.
*   **Physical Hazards:**  No physical hazards exist. Students should maintain a clean and organized workspace.
*   **Ergonomics:** Ensure a comfortable posture while using the computer. Take short breaks to prevent eye strain and fatigue. [INSTRUCTOR: Monitor students for potential physical strain.]
*   **Data Security:** Do not share the MATLAB script with unauthorized individuals.
*   **Computer Safety:** Avoid spilling liquids on the computer. [INSTRUCTOR: Ensure proper ventilation.]

**5. Procedure (7 steps)**

1.  **Open MATLAB:** Launch MATLAB and ensure the provided script is available.
2.  **Run the Script:**  Execute the MATLAB script. Observe the output in the Command Window.
3.  **Parameter Adjustment (Optional):**  [INSTRUCTOR: Demonstrate how to modify `dt` and `noise_std` to observe their effects on the simulated robot's movement].  Experiment with changing the time step (`dt`) and standard deviation of the noise (`noise_std`) and observe the changes in the simulated robot’s position.
4.  **Record Output:** Carefully record the position values displayed in the Command Window for each time step.
5.  **Data Collection (Initial Observation):**  Note the initial position of the robot (t=0) and any immediately apparent trends in its movement.
6.  **Parameter Exploration:**  [INSTRUCTOR: Guide students through modifying the parameters, discussing the effect of noise on the robot’s trajectory.]
7.  **Repeat Steps 6 and 7:**  Repeat steps 6 and 7 multiple times, noting the variations in the robot’s position.

**6. Data Collection (Table Template)**

| Time Step (t) | Position (x) |
|---------------|--------------|
| 0             |              |
| 1             |              |
| 2             |              |
| 3             |              |
| ...           |              |
| 100           |              |

**7. Analysis Questions (5 questions)**

1.  How does the noise term (`w`) influence the robot's position over time? Describe the pattern of variation.
2.  What is the impact of the time step (`dt`) on the smoothness of the robot's trajectory?  (Consider the effect of smaller versus larger `dt` values).
3.  Explain how the state equation *x<sub>t+1</sub> = f(x<sub>t</sub>, u<sub>t</sub>, w<sub>t</sub>)* represents the robot’s movement. Identify the components of the equation.
4.  If the noise standard deviation were set to zero, what would the robot's trajectory look like?
5.  Discuss how this simulated environment relates to real-world sensor data affecting a robot's perception and navigation.

**8. Expected Results (3 results)**

*   **Varied Position:** The robot's position will fluctuate around the initial position due to the noise term. The magnitude of the fluctuations will depend on the `noise_std` value.
*   **Time Step Dependence:**  A smaller `dt` will produce a smoother trajectory, while a larger `dt` will lead to a more erratic and less smooth movement.
*   **Trajectory Visualization (Visual Aid):**  A plot of the robot's position over time, demonstrating the effects of noise and time step on the trajectory.  [INSTRUCTOR: Provide a sample plot for comparison.]