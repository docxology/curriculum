# Variational Inference - Laboratory Exercise 4

## Lab Focus: Evidence Lower Bound

---

## Lab 4: Evidence Lower Bound – Mean Field Approximation

**Module:** Variational Inference
**Lab Number:** 4
**Lab Focus:** Evidence Lower Bound

**1. Brief Background (98 words)**

This laboratory exercise explores the fundamental concept of the Evidence Lower Bound (ELBO) within the context of Variational Inference. Following a lecture introduction to variational inference and intractable posterior distributions, we’ll investigate how the ELBO provides a tractable, lower bound on the marginal likelihood, or evidence, P(X). The ELBO directly relates to the Mean Field Approximation, where we assume the approximate posterior distribution factors into independent components. This simplification drastically reduces the computational burden while still providing a useful approximation of the true posterior, facilitating learning in complex models. The ELBO allows us to explore the impact of different approximation strategies.

**2. Lab Objectives (4 bullet points)**

*   Implement a simplified ELBO calculation to illustrate its relationship to the likelihood and prior.
*   Analyze the impact of varying the number of factors in a simple Gaussian Mixture Model approximation.
*   Calculate the ELBO for a given dataset and observe its relationship to the log-evidence.
*   Understand how the ELBO provides a lower bound on the true marginal likelihood.
*   Compare and contrast the behavior of different factorizations within the Mean Field Approximation.

**3. Materials and Equipment**

*   **Software:** Python 3.7+ with NumPy, SciPy, Matplotlib
*   **Hardware:** Laptop with sufficient processing power.
*   **Datasets:**
    *   Synthetic Dataset 1: A dataset generated from a 2-component Gaussian Mixture Model (GMM) with known parameters (μ1 = 1.0, σ1 = 0.5; μ2 = 5.0, σ2 = 1.0).
    *   Synthetic Dataset 2: A dataset generated from a 3-component GMM with known parameters (μ1 = 0.5, σ1 = 0.4; μ2 = 2.0, σ2 = 0.6; μ3 = 4.0, σ3 = 0.8).
*   **Calculators:** Standard scientific calculators.
*   **Optional:** Graph paper

**4. Safety Considerations (⚠️)**

*   **Data Handling:** All synthetic datasets are created within the software environment and pose no biological or chemical hazards.
*   **Computer Use:** Follow standard computer hygiene practices. Ensure proper ventilation.
*   **Time-Sensitive Step (15 minutes):**  Data generation and model fitting require continuous processing. Monitor system performance to avoid overheating or crashes. [INSTRUCTOR] – Monitor student progress closely during this step.

**5. Procedure (7 steps)**

1.  **Setup Environment:**  Install and configure Python environment with necessary libraries (NumPy, SciPy, Matplotlib).
2.  **Data Generation:**  Generate Synthetic Dataset 1 using the 2-component GMM. Record the true parameters (μ1, σ1, μ2, σ2) and the generated data points (X).
3.  **ELBO Calculation (2-factor):** Implement the ELBO calculation for the 2-factor Gaussian Mixture Model approximation.  Assume the two factors are independent.  Calculate the ELBO using the formula: ELBO = E[log P(X|θ)] – KL Divergence (between the approximation and the prior).  [INSTRUCTOR] – Provide a simplified ELBO calculation code snippet for students to adapt.
4.  **ELBO Calculation (3-factor):**  Repeat Step 3, this time using a 3-factor Gaussian Mixture Model approximation.
5.  **Data Generation (Dataset 2):** Generate Synthetic Dataset 2 using the 3-component GMM.
6.  **ELBO Calculation (Dataset 2):** Calculate the ELBO for the 3-factor approximation of Dataset 2.
7.  **Comparison:** Compare the ELBO values for the 2-factor and 3-factor approximations of Dataset 1 and Dataset 2.

**6. Data Collection**

| Dataset | Number of Factors | ELBO Value (Step 6) | KL Divergence Value (Step 6) | Log Evidence Estimate (Step 6) |
| :------- | :---------------- | :------------------ | :------------------------- | :----------------------------- |
| Dataset 1 | 2                |                     |                            |                                 |
| Dataset 1 | 3                |                     |                            |                                 |
| Dataset 2 | 2                |                     |                            |                                 |
| Dataset 2 | 3                |                     |                            |                                 |

**7. Analysis Questions (5 bullet points)**

*   How does increasing the number of factors in the Mean Field Approximation affect the ELBO value?  Does it always increase?
*   Explain the relationship between the ELBO and the log-evidence (P(X)). What does it mean for the ELBO to be a lower bound?
*   Describe the impact of the KL Divergence term on the ELBO.  How does it relate to the complexity of the approximation?
*   Consider a scenario where the true posterior is highly complex (e.g., multiple, correlated factors).  Would the Mean Field Approximation still be a reasonable choice? Explain.
*   If the ELBO consistently decreases with each added factor, does this necessarily indicate a better approximation? Explain why or why not.

**8. Expected Results (3 points)**

Students should observe that as the number of factors increases in the Mean Field Approximation, the ELBO value generally increases, though this isn't always a strict linear relationship. The increase in the ELBO is due to capturing more of the true posterior distribution's complexity. The KL Divergence term will also increase, reflecting the growing difference between the approximate posterior and the true posterior.  The log-evidence estimate will be consistently lower than the ELBO. The results highlight the trade-off between accuracy and computational cost in the Mean Field Approximation. [INSTRUCTOR] – Encourage students to discuss the limitations of the Mean Field Approximation and consider alternative approaches.