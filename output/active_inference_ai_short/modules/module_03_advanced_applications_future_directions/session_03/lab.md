# Advanced Applications & Future Directions - Laboratory Exercise 3

## Lab Focus: Robotics and Active Inference

---

## Lab 3: Collaborative Navigation with Multi-Agent Active Inference

**Module:** Advanced Applications & Future Directions
**Lab Number:** 3
**Lab Focus:** Robotics and Active Inference

**1. Brief Background:**

This laboratory exercise builds upon the lecture’s discussion of Active Inference and Shared World Models. We will explore how multiple robots can collaboratively navigate a simple environment, mirroring the principles of collective free energy minimization.  Each robot will operate with a limited perceptual input – solely visual – and will be tasked with reaching a target location, relying on shared belief updates to coordinate their actions and avoid collisions.  The exercise highlights the challenges of building and maintaining a shared world model in a multi-agent setting.

**2. Lab Objectives:**

*   Program two simple robots to navigate a 2D environment.
*   Implement a basic Shared World Model based on agent positions.
*   Observe and record the robots' behaviors during collaborative movement.
*   Analyze the impact of individual action choices on the overall group performance.
*   Modify parameters (e.g., precision weighting) to assess their effect on coordination.

**3. Materials and Equipment:**

*   **Robots:** Two identical mobile robots (e.g., Thymio II robots or comparable platforms with camera and motor control).
*   **Software:** Robot control software (ThymioLive or equivalent) – version 4.4 or later.
*   **Sensors:** Each robot’s integrated camera (resolution: 320x240 pixels).
*   **Power Supplies:** Robot-specific power adapters (12V DC).
*   **Communication:** USB cables for robot-computer connection.
*   **Physical Environment:** A 1m x 1m x 1m rectangular space, marked with tape for clear boundaries.  A distinct target location (e.g., a colored marker) positioned 0.5m from one edge of the space.
*   **Measuring Tape:** For accurate placement of the target and robots.

**4. Safety Considerations:**

⚠️ **Physical Hazard:**  The lab space contains a small, defined area. Students should maintain a safe distance from the robots and other students during operation.  Avoid sudden movements that could cause the robots to collide.
⚠️ **Electrical Hazard:** Ensure all power cords are in good condition and free from damage. Do not operate the robots near water.
⚠️ **Data Security:** Robots are connected to a computer. Ensure all software is updated and free of malware. [INSTRUCTOR] – Verify robot network connectivity prior to commencement.
PPE: Safety Goggles, Gloves (optional – for handling cables).

**5. Procedure:**

1.  **Setup (15 minutes):** Place the target marker at the designated location.  Connect each robot to the computer using the USB cable. Power on both robots and the computer.
2.  **Robot Initialization (10 minutes):** Using the robot control software, initialize each robot. Ensure it recognizes the camera and can navigate within the defined boundaries.
3.  **Individual Navigation (20 minutes):** Program each robot with the following simple navigation algorithm:
    *   **Perception:** Capture an image from the camera.
    *   **World Model Update:** Calculate the distance to the target marker in the image.
    *   **Action:** Move towards the target marker, adjusting speed to maintain a target distance (e.g., 0.1m per step).
4.  **Precision Weighting Experiment (25 minutes):**  Modify the robot control software to introduce a ‘precision weighting’ parameter (e.g., 0.5, 1.0, 1.5) that scales the distance-to-target value before it's used for action.  Observe the robots’ behavior with each weighting value.
5.  **Data Collection (5 minutes):**  Record observations using the table below.

**6. Data Collection:**

| Robot | Time (s) | Distance to Target | Speed (cm/s) | Observed Behavior (e.g., “Rapid oscillations,” “Slow, steady approach,” “Collision”) |
| :----: | :------: | :-----------------: | :----------: | :---------------------------------------------------------------------- |
| Robot 1 | 0        |                    |             |                                                                         |
| Robot 1 | 5        |                    |             |                                                                         |
| Robot 1 | 10       |                    |             |                                                                         |
| ...    | ...     | ...                | ...         | ...                                                                        |
| Robot 2 | 0        |                    |             |                                                                         |
| Robot 2 | 5        |                    |             |                                                                         |
| Robot 2 | 10       |                    |             |                                                                         |

**7. Analysis Questions:**

1.  How does the precision weighting parameter influence the robots’ coordinated movement?  Explain the observed effects.
2.  Why might the robots initially exhibit chaotic behavior despite using a shared world model?  Relate this to the concept of ‘surprise’ and the exploration of the environment.
3.  How could the Shared World Model be improved to enhance the robots’ ability to navigate efficiently and reliably?
4.  What are the limitations of this simple Shared World Model, and what additional elements might be needed for more complex multi-agent scenarios?
5. What are the practical implications of implementing such a shared world model in a real-world robotics system (e.g., autonomous warehouse robots)?

**8. Expected Results:**

Students should observe that without precise weighting, the robots’ actions are initially unpredictable, leading to rapid oscillations and potential collisions. As the precision weighting increases, the robots’ movements become more coordinated, allowing them to converge towards the target.  The observed chaotic behavior is attributed to the individual robots’ exploration and the ‘surprise’ inherent in the unknown environment.  The effectiveness of the Shared World Model will likely be limited by the simplistic perception and action capabilities of the robots.  Further improvements to the shared world model would likely require incorporating more robust perceptual processing and action planning strategies.