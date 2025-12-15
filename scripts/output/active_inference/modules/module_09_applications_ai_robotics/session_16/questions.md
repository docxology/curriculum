# Applications: AI & Robotics - Comprehension Questions

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

**Question 2:** Which of the following best describes a perception-action loop?
A) A pre-programmed sequence of events executed by a robot.
B) A continuous cycle where a robot senses its environment, processes that information, and then takes an action based on it.
C) A static map of the environment that a robot uses to navigate.
D) A single, isolated command that instructs a robot to perform a specific task.
**Answer:** B
**Explanation:** A perception-action loop is a fundamental concept in robotics and AI, representing the iterative process of sensing, planning, and acting, essential for adaptive systems.

**Question 3:** What is the main purpose of using a simulated environment like Gazebo for robot navigation experiments?
A) To create a realistic representation of a physical workspace.
B) To reduce the cost and risk of experimentation with real robots.
C) To automatically optimize robot movement patterns.
D) To directly control robot hardware in real-time.
**Answer:** B
**Explanation:** Gazebo provides a safe and controlled virtual environment for testing robot algorithms and sensor integration before deployment on physical robots, minimizing potential damage or disruption.

**Question 4:**  Why is adaptive navigation crucial for robots operating in unstructured environments?
A) It allows robots to always follow the most direct route.
B) It enables robots to adjust their behavior based on changes in the environment.
C) It guarantees perfect obstacle avoidance at all times.
D) It eliminates the need for any sensor input.
**Answer:** B
**Explanation:** Adaptive navigation is critical because real-world environments are dynamic and unpredictable, requiring robots to continuously process sensory data and modify their actions accordingly.

**Question 5:**  What does “sampling strategies” refer to in the context of robot navigation?
A) The use of random movements to explore an area.
B) Selecting specific locations or areas to investigate based on sensor data.
C)  Prioritizing pre-determined routes regardless of obstacles.
D)  Ignoring sensor data to simplify navigation.
**Answer:** B
**Explanation:** Sampling strategies involve choosing which areas to explore based on available data, such as sensor readings, allowing robots to efficiently gather information about their surroundings.

**Question 6:** Briefly explain the role of a simulated ultrasonic sensor in a robot navigation lab?
**Answer:** A simulated ultrasonic sensor provides distance measurements to nearby objects, feeding this data back into the robot’s control system. This allows the robot to determine obstacle locations and adjust its movement to avoid collisions. Key points include distance measurement and collision avoidance.

**Question 7:**  Describe one potential challenge to adaptive navigation that a robot might encounter.?
**Answer:** A significant challenge is unpredictable human behavior. A robot programmed to follow a hallway might become stuck if someone unexpectedly walks across its path, demonstrating the need for robust adaptation to unforeseen circumstances.

**Question 8:**  How does the use of a simulated environment support the learning objectives of this lab exercise?
**Answer:** The simulated environment allows students to experiment with different algorithms and sensor configurations without the risk of damaging a physical robot or disrupting a real-world workspace. This fosters a safe and iterative learning process.

**Question 9:** Explain, in your own words, how a robot could use a simulated ultrasonic sensor to build a basic understanding of its surroundings.?
**Answer:** The robot would constantly send out ultrasonic sound waves and measure the time it takes for them to bounce back. This data is then translated into distance measurements, creating a "map" of the robot's immediate environment, enabling it to identify obstacles and plan a safe path.

**Question 10:**  Imagine a robot navigating a room. What steps would a perception-action loop involve in the process of avoiding a moving chair?
**Answer:** The robot would sense the chair's movement via its sensors (likely ultrasonic), process this information to determine the chair's trajectory and speed, then adjust its path (e.g., turn, slow down) to avoid a collision, and repeat this cycle continuously.