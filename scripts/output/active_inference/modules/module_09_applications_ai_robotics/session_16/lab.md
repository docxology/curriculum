# Applications: AI & Robotics - Laboratory Exercise 16

## Lab Focus: Perception-Action Loops

---

**Module: Applications: AI & Robotics**
**Lab Number: 16**
**Lab Focus: Perception-Action Loops**

**1. Brief Background (98 words)**

This laboratory exercise directly builds upon the lecture’s discussion of robot navigation and the importance of perception-action loops. Students will implement a simplified exploration algorithm, mirroring the core principles of adaptive robot behavior. Utilizing a simulated environment and a basic sensor interface, participants will learn how a robot can dynamically adjust its movements based on incoming data – essentially creating a closed loop. The exercise emphasizes the iterative process of sensing, planning, and acting, a fundamental component of autonomous systems design. Understanding these loops is crucial for developing robots capable of robust navigation in unpredictable environments.

**2. Lab Objectives (4 bullet points)**

*   Implement a basic “wall following” algorithm using a simulated sensor input.
*   Modify the algorithm’s parameters (e.g., sensor sensitivity, turning radius) to observe the impact on robot behavior.
*   Analyze the resulting movement patterns and identify potential challenges to adaptive navigation.
*   Design a simple adjustment to the algorithm to improve obstacle avoidance.
*   Document the experimentation process, including parameter settings and observed results.

**3. Materials and Equipment (Organized by Category)**

*   **Software:** Gazebo Simulator (Version [INSTRUCTOR – Specify Version]) - Downloadable from [INSTRUCTOR – Provide Link]
*   **Robot Model:** MobileRobotSim – Model [INSTRUCTOR – Specify Model Name] (Pre-configured within Gazebo)
*   **Sensor Interface:** Simulated Ultrasonic Sensor – Range: 20cm - 1 meter, Accuracy: +/- 2cm.  Simulated data stream output is a floating-point number representing distance in cm.
*   **Computer:** Desktop or Laptop with sufficient RAM (8GB minimum) – Operating System: Windows 10/11 or Linux (Ubuntu 20.04 recommended).
*   **Data Logging Software:** Text editor or spreadsheet software (e.g., Microsoft Excel, Google Sheets) - for recording observations.

**4. Safety Considerations (⚠️)**

⚠️ **Physical Hazards:** The Gazebo simulator operates on a computer. Ensure the computer is placed on a stable surface and is not subjected to excessive vibration. Monitor the computer temperature during prolonged use.
⚠️ **Time-Sensitive Step:**  Do not operate the simulated robot at full speed for extended periods. Reduce simulated robot speed to 50% during initial testing.
⚠️ **Electrical Safety:** Do not expose the computer to water or excessive moisture.
⚠️ **PPE Requirements:** Safety Glasses – Required at all times during the experiment.

**5. Procedure (7 Steps)**

1.  **Launch Gazebo:** Start the Gazebo simulator.
2.  **Load Robot Model:**  Select the “MobileRobotSim – Model [INSTRUCTOR – Specify Model Name]” robot model from the Gazebo model library.
3.  **Configure Sensor:**  Ensure the simulated Ultrasonic Sensor is connected to the robot model within Gazebo. Verify the sensor range is set to 20cm - 1 meter.
4.  **Set Initial Parameters:** In the Gazebo world editor, set the robot’s initial position to (0, 0, 0). Set the robot’s speed to 1 m/s.
5.  **Implement Wall Following:**  Within the Gazebo world editor, add a virtual "wall" at the position (2.5m, 0, 0).  Implement the following Python code within the Gazebo world editor to control the robot:
    ```python
    import time

    speed = 1.0
    sensitivity = 0.5
    turning_radius = 0.5
    wall_distance = 0.0 #Initial value
    while True:
        wall_distance = get_sensor_data() #Simulated sensor function
        if wall_distance < turning_radius:
            speed = -speed
        time.sleep(0.1)
    ```
6.  **Observe and Adjust:**  Run the simulation. Observe the robot’s behavior as it attempts to follow the virtual wall. Adjust the `sensitivity` parameter (values between 0.1 and 1.0) to observe its effect on the robot’s response.
7.  **Document Results:** Record the sensor values, robot speed, and observed behavior in the data collection table below.

**6. Data Collection (Markdown Table Template)**

| Time (s) | Sensor Distance (cm) | Robot Speed (m/s) | Observed Behavior | Parameter Settings (Sensitivity) |
|---|---|---|---|---|
| 0 | [INSTRUCTOR – Initial Value] | 1.0 |  | 0.5 |
| 0.1 | [INSTRUCTOR – Value] | 1.0 |  | 0.5 |
| 0.2 | [INSTRUCTOR – Value] | 1.0 |  | 0.5 |
| 0.3 | [INSTRUCTOR – Value] | 1.0 |  | 0.5 |
| ... | ... | ... | ... | ... |

**7. Analysis Questions (5 Questions)**

1.  How did changing the sensor sensitivity affect the robot’s ability to maintain a constant distance from the virtual wall?
2.  Explain why a smaller turning radius might lead to erratic behavior – what challenges are the robot encountering?
3.  What are the limitations of this simulated sensor data, and how might these limitations impact a real robot navigating a complex environment?
4.  Describe a scenario where a real ultrasonic sensor might provide inaccurate data (e.g., reflection from a curved surface).
5.  How could the “wall following” algorithm be improved to handle more complex scenarios (e.g., multiple walls, obstacles)?

**8. Expected Results (2 Statements)**

Students should observe that increasing the sensor sensitivity causes the robot to oscillate closer to the virtual wall. Conversely, decreasing the sensitivity will result in the robot moving further away. The experiment should demonstrate that changing the parameters affects the robot’s ability to maintain a stable movement pattern, highlighting the core principles of adaptive control.