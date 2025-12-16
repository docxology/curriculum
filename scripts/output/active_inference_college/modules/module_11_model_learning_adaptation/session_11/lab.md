# Model Learning & Adaptation - Laboratory Exercise 11

## Lab Focus: Maximum Likelihood Estimation

---

**Module: Model Learning & Adaptation**
**Lab Number: 11**
**Lab Focus: Maximum Likelihood Estimation**

**1. Brief Background (87 words)**

This laboratory exercise builds upon the lecture’s introduction to parameter estimation and the iterative process of minimizing the loss function. We will explore Maximum Likelihood Estimation (MLE), a core technique used to find parameter values that best explain the observed data. MLE seeks the parameter values that maximize the probability of observing the dataset. This lab focuses on a simplified example of a single-parameter exponential decay model. Understanding MLE is crucial for adapting models to real-world systems, ensuring their predictive power is optimized.

**2. Lab Objectives**

*   Implement a simple exponential decay model.
*   Estimate the decay rate parameter using MLE.
*   Analyze the relationship between the decay rate and the observed data.
*   Evaluate the convergence of the parameter estimation process.

**3. Materials and Equipment**

*   **Software:** MATLAB or Python (with NumPy, SciPy) - [INSTRUCTOR] suggests using a spreadsheet for easier initial experimentation.
*   **Data Set:** Prepared dataset of exponential decay values – 100 data points, generated with a decay rate of 0.8. Data values will range from 10 to 0.1.
*   **Spreadsheet Software:** Microsoft Excel or Google Sheets.
*   **Calculators:** Standard scientific calculators.

**4. Safety Considerations (⚠️)**

⚠️ **Biological Hazard:** The data set may contain simulated bacterial growth, posing a potential biohazard.
*   Strictly adhere to all aseptic techniques.
*   Dispose of all materials containing simulated bacterial growth in designated biohazard containers.
*   Wash hands thoroughly with soap and water after completing the lab.
⚠️ **Computer Safety:** Avoid excessive strain on computer hardware.  Ensure proper ventilation while using the computer.
*   Avoid spilling liquids on the equipment.
*   Do not operate the equipment with wet hands.

**5. Procedure**

1.  **Data Loading:** Load the pre-generated exponential decay data into your chosen software (MATLAB/Python/Spreadsheet).
2.  **Model Definition:** Define the exponential decay model function in your software: `y = a * exp(-b * x)`, where ‘a’ is the initial value and ‘b’ is the decay rate parameter we will estimate.
3.  **Initial Guess:** Set an initial guess for the decay rate parameter ‘b’ (e.g., b = 0.5).
4.  **Loss Function Calculation:** Implement a simple loss function (e.g., Mean Squared Error - MSE) to quantify the difference between the model’s predicted values and the actual data values. MSE = Sum((actual_i - predicted_i)^2) / N, where N is the number of data points.
5.  **Parameter Update:** Using a simple iterative algorithm (e.g., gradient descent), adjust the value of ‘b’ based on the gradient of the loss function. The gradient indicates the direction of steepest descent.  Implement a learning rate (e.g., 0.01) to control the step size.  Update ‘b’ as:  `b = b - learning_rate * gradient_of_loss_function_with_respect_to_b`.
6.  **Iteration:** Repeat steps 5 until the loss function converges to a minimum. Monitor the loss value over iterations. [INSTRUCTOR] recommends running the iteration process 50 times.
7.  **Documentation:** Record the initial guess for 'b' and the final value of 'b' achieved after convergence.

**6. Data Collection**

| Iteration | Loss Value | Decay Rate (b) |
| :-------: | :--------: | :------------: |
|      0    |  [VALUE]  |     0.5       |
|      1    |  [VALUE]  |     0.55       |
|      2    |  [VALUE]  |     0.58       |
|   ...     |   ...     |      ...      |
|     50    |  [VALUE]  |     0.78       |

*Record the loss value and final decay rate ‘b’ for each iteration.*

**7. Analysis Questions**

1.  How did the loss function change over iterations? What does this indicate about the convergence of the parameter estimation process?
2.  What is the relationship between the learning rate and the speed of convergence?  How might a larger learning rate affect the outcome?
3.  How accurately did the estimated decay rate ‘b’ capture the true value (0.8)?  Discuss potential sources of error.
4.   If the loss function plateaued, what does this indicate about the fit of the model to the data?

**8. Expected Results**

Students should observe that the loss function steadily decreases over iterations, indicating that the model’s fit to the data is improving.  The final estimated decay rate ‘b’ will converge to a value close to 0.8 (within a tolerance of 0.05).  A larger learning rate will cause faster initial convergence but may overshoot the optimal value, leading to instability. The loss function should converge to a minimum, demonstrating the model's best fit to the data.  The convergence rate may vary depending on the learning rate selected. [INSTRUCTOR] will monitor convergence rate for each group.