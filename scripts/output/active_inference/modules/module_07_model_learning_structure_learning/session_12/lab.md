# Model Learning & Structure Learning - Laboratory Exercise 12

## Lab Focus: Bayesian Updating of Models

---

**Module: Model Learning & Structure Learning**
**Lab Number: 12**
**Lab Focus: Bayesian Updating of Models**

**1. Brief Background (98 words)**

This lab builds upon the foundational concepts discussed in the lecture concerning parameter estimation and the role of model parameters (θ) in predicting phenomena. We will explore Bayesian updating, a cornerstone of model learning. Bayesian updating allows us to revise our initial parameter estimates based on new data, incorporating prior beliefs with the observed data. This iterative process is central to building robust and accurate models. Specifically, we will utilize a simple exponential decay model to demonstrate how observed data can shift our belief regarding the decay rate, moving from a prior estimate to a posterior estimate, representing a refined understanding of the underlying process. The core principle is that Bayesian updating leverages probability theory to quantify uncertainty and refine model parameters.

**2. Lab Objectives (4 bullet points)**

*   Calculate prior parameter values for an exponential decay model.
*   Collect observed data representing decay rates.
*   Apply the Bayesian updating rule to calculate posterior parameter values.
*   Analyze the impact of new data on the model’s parameter estimates.

**3. Materials and Equipment**

*   **Software:**  Microsoft Excel (or equivalent spreadsheet program)
*   **Calculators:** Scientific calculators (TI-30XIIS or equivalent)
*   **Data Logger:**  A pre-programmed data logger (capable of generating random numbers within a defined range) – Set to generate 20 data points.
*   **Printouts:**  Bayesian Updating Rule Worksheet (provided – includes formula for posterior distribution), Data Analysis Template (provided).
*   **Reference Materials:**  Lecture slides on Bayesian Updating.

**4. Safety Considerations (⚠️)**

*   **Electrical Safety:**  Ensure all equipment is properly grounded and that electrical cords are not frayed or damaged.  Do not operate equipment near water.
*   **Data Logger Calibration:** Verify data logger accuracy before commencing the experiment. [INSTRUCTOR] – Calibrate data logger following manufacturer's instructions.
*   **Software Use:**  Exercise caution when using spreadsheet software. [INSTRUCTOR] - Avoid accidental file deletion or overwriting.
*   **No Chemical Hazards:** This lab contains no chemical hazards.

**5. Procedure (7 steps)**

1.  **Initial Parameter Guess:** Using your calculator, set initial values for the exponential decay parameter, λ (lambda), based on a prior belief about the decay rate. Record this initial value in the Data Analysis Template.  Assume an initial λ = 0.5.
2.  **Data Generation:** Program the data logger to generate 20 random numbers between 0 and 1. These numbers represent observed decay rates.
3.  **Model Simulation:** Using Excel, simulate the exponential decay function:  y = A * exp(-λt), where ‘t’ ranges from 0 to 1.  Use the initial value of λ. Record the simulated data (y values).
4.  **Calculate the Error:** Compute the squared error between the simulated data and the observed data. Calculate the mean squared error (MSE). [INSTRUCTOR] - Provide a template for MSE calculation.
5.  **Bayesian Updating:** Apply the Bayesian updating rule:
     *   *Prior* = Initial λ
     *   *Posterior* =  [Prior * (Number of Observations)] / [Prior * (Number of Observations) + MSE]
     Record the posterior value of λ.
6.  **Repeat Steps 4 and 5:** Generate a new set of 20 random numbers and repeat steps 4 and 5.
7.  **Compare Results:** Analyze the changes in λ between iterations.

**6. Data Collection (Template)**

| Iteration | λ (Initial) | Observed Decay Rate (Random Number) | y = A * exp(-λt) | MSE | λ (Posterior) |
| :-------- | :--------- | :------------------------------------ | :---------------- | :--- | :------------- |
| 1         | 0.5        | [PLACEHOLDER]                         | [PLACEHOLDER]      |      | [PLACEHOLDER] |
| 2         |            |                                       |                   |      |               |
| 3         |            |                                       |                   |      |               |
| …         |            |                                       |                   |      |               |
| 20        |            |                                       |                   |      |               |

**7. Analysis Questions (4 questions)**

1.  How did the posterior value of λ change between the initial guess and the first iteration? Explain the reasoning behind this change.
2.  What does the Bayesian updating rule mathematically represent in terms of incorporating new evidence?
3.  How does the observed data influence the model parameter estimates?
4.  If the observed data consistently showed a faster decay rate than the initial guess, how would you interpret this in the context of the exponential decay model?

**8. Expected Results (What students should observe and why)**

Students should observe that the posterior value of λ will decrease (become more negative) with each iteration. This decrease reflects the model adapting to the observed data, which suggests a faster decay rate than the initial prior assumption. The Bayesian updating rule quantitatively incorporates the new data, reducing the uncertainty associated with the decay rate. The magnitude of the change will be influenced by the variability in the generated data. [INSTRUCTOR] – Discuss the concept of convergence in Bayesian updating.