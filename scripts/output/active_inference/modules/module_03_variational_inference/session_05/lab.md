# Variational Inference - Laboratory Exercise 5

## Lab Focus: ELF Formulation

---

## Lab 5: ELF Formulation – Evidence Lower Bound

**1. Brief Background (98 words)**

This laboratory exercise builds upon the foundational concepts of Bayesian inference and the challenges of exact posterior inference. Following the lecture introduction to variational inference and the concept of the Evidence Lower Bound (ELF), we’ll explore the ELF formulation as a lower bound on the marginal likelihood. The marginal likelihood, L(θ|x), dictates the overall probability of our model given the observed data. The ELF – log q(θ) – offers a tractable alternative to calculating this integral, providing a crucial step in approximating the true posterior distribution using variational inference. The core of this lab is hands-on experimentation with a simplified model and a numerical optimization routine to demonstrate the ELF minimization process.

**2. Lab Objectives (4 bullet points)**

*   Implement a simplified model and generate synthetic data.
*   Define a variational distribution (q(θ)) for the model parameters.
*   Calculate the Evidence Lower Bound (ELF) for a given variational distribution.
*   Optimize the variational distribution parameters to minimize the ELF.

**3. Materials and Equipment**

*   **Software:** Python 3.9+, NumPy, SciPy, Matplotlib
*   **Hardware:** Laptop with sufficient RAM (8GB minimum)
*   **Data Generation Tool:**  Pre-written Python script for generating synthetic data (provided by [INSTRUCTOR])
*   **Optimization Library:** SciPy’s optimization routines (minimize_scalar)
*   **Notebook Environment:** Jupyter Notebook or Google Colaboratory
*   **Calibration Thermometer:** Accuracy ± 0.5°C

**4. Safety Considerations (⚠️)**

*   **Data Generation:** The synthetic data generation script contains no hazardous materials. However, prolonged computer use can lead to eye strain. Take frequent breaks (every 20 minutes) and follow the 20-20-20 rule (look at an object 20 feet away for 20 seconds).
*   **Software Usage:** Ensure all software components are updated to the latest stable versions to mitigate potential bugs.
*   **Temperature Monitoring:**  Monitor room temperature to ensure it remains within a comfortable range (18-24°C). Extreme temperatures can affect electronic equipment performance.
*   **Electrical Safety:**  Ensure all electrical equipment is properly grounded and avoid spills near electrical outlets.

**5. Procedure (7 numbered steps)**

1.  **Load Data Generation Script:**  Execute the provided Python script ([INSTRUCTOR - provide script name]) to generate a dataset with 1000 data points.  The script will create a synthetic dataset with two parameters, 'θ1' and 'θ2', and a corresponding likelihood function.
2.  **Define Variational Distribution:**  Initialize a prior distribution for the parameters θ.  Begin with a Gaussian prior: q(θ) = N(θ| μ=0, σ=1).  Record the initial values of μ and σ.
3.  **Calculate ELF:**  Implement a function to calculate the Evidence Lower Bound (ELF) for the given q(θ). The ELF is calculated as log q(θ) evaluated at the current parameter values. Use the provided Python template as a starting point, calculating the log-likelihood and incorporating the prior distribution.
4.  **Implement Optimization:** Utilize SciPy’s `minimize_scalar` function to find the parameter values that minimize the ELF.  Set the objective function to the ELF and use a suitable optimization algorithm (e.g., ‘Brent’). Set the bounds for θ1 and θ2 to [-1, 1] to constrain the search space.
5.  **Run Optimization:** Execute the optimization process. Monitor the objective function value (ELF) during the optimization, observing its decrease.
6.  **Record Final Parameters:**  After the optimization completes, record the final values of θ1 and θ2.
7. **Temperature Monitoring:**  Check the ambient temperature using a calibrated thermometer. Record the temperature.

**6. Data Collection (Template)**

| Parameter | Initial Value | Final Value | Temperature (°C) |
|---|---|---|---|
| θ1 | [INSTRUCTOR - Placeholder] | [INSTRUCTOR - Placeholder] | [INSTRUCTOR - Placeholder] |
| θ2 | [INSTRUCTOR - Placeholder] | [INSTRUCTOR - Placeholder] | [INSTRUCTOR - Placeholder] |
| ELF Value (Iteration) | [INSTRUCTOR - Placeholder] | [INSTRUCTOR - Placeholder] | [INSTRUCTOR - Placeholder] |

**7. Analysis Questions (5 questions)**

1.  Describe the relationship between the optimization process and the minimization of the Evidence Lower Bound (ELF).
2.  How does the choice of prior distribution (q(θ)) affect the final values of the model parameters?
3.  Explain the significance of the ELF as a lower bound on the marginal likelihood.
4.  What would happen if you used a different optimization algorithm to minimize the ELF?
5.  How does the process of minimizing the ELF relate to the concept of approximating the true posterior distribution?

**8. Expected Results (3 Observations)**

1.  The optimization process will iteratively adjust the parameters (θ1 and θ2) to minimize the ELF. The ELF value will continuously decrease as the optimization progresses.
2.  The final values of θ1 and θ2 will be significantly different from the initial values due to the optimization process.
3.  The final ELF value will be a lower bound on the marginal likelihood – demonstrating that we have found a variational distribution that provides a tractable lower bound on the true posterior.