# Bayesian Inference – Model Specification - Laboratory Exercise 4

## Lab Focus: Likelihood ratio test

---

**Module: Bayesian Inference – Model Specification**
**Lab Number: 4**
**Lab Focus: Likelihood Ratio Test**

**1. Brief Background (92 words)**

Following our discussion on Bayesian inference and model specification, this lab introduces a key method for comparing candidate models: the likelihood ratio test.  We’ve learned that simply choosing the model with the highest posterior probability isn’t sufficient. The likelihood ratio test provides a formal statistical comparison by examining the ratio of the likelihoods of two models.  This ratio, when greater than 1, suggests that the more complex model provides better evidence for the data. We will explore the theoretical foundation and practical application of this test, alongside introductions to the AIC and BIC metrics. This lab will solidify your understanding of model selection in a Bayesian framework. [INSTRUCTOR: Briefly demonstrate the concept of likelihood ratio test on a single parameter case – e.g., comparing a normal distribution to a skewed distribution.]

**2. Lab Objectives (4 bullet points)**

*   Calculate the likelihood ratio between two candidate models.
*   Interpret the results of the likelihood ratio test.
*   Apply the likelihood ratio test to a simulated dataset.
*   Compare the results with those derived from AIC and BIC calculations.

**3. Materials and Equipment**

*   **Software:** R (version 4.3.2 or later), RStudio Desktop
*   **Data Generation Script:** Provided (R script to generate simulated datasets)
*   **Calculators:** Scientific or graphing calculators.
*   **Worksheets:** Printed worksheets for data recording and calculations.
*   **Computer Access:** Each student needs access to a computer with R installed.

**4. Safety Considerations (⚠️)**

*   **Computer Safety:**  Ensure proper ventilation when using computers for extended periods.  Report any electrical issues immediately.
*   **Data Handling:** All data is simulated, eliminating biological or chemical hazards.
*   **Software Integrity:**  Use only the provided R script. Do not modify without [INSTRUCTOR] approval.
*   **Eye Protection:** Wear safety goggles at all times during the experiment.
*   **Time Sensitivity:**  No time-sensitive steps.

**5. Procedure (7 steps)**

1.  **Load the R Script:**  Open the provided R script in RStudio. [INSTRUCTOR: Ensure students understand how to execute R code.]
2.  **Run the Data Generation Script:** Execute the script to generate two simulated datasets: a simple linear model and a more complex model including a quadratic term.  Observe the dataset printed to the console.
3.  **Define Model Likelihoods:**  Within R, define the likelihood functions for both models.  The script provides pre-defined functions; verify these.
4.  **Calculate Likelihood Ratio:**  Using R, calculate the likelihood ratio for each model.  Record the ratio in your worksheet.
5.  **Interpret the Ratio:**  Discuss the calculated likelihood ratio.  Does the more complex model have a higher likelihood ratio? Explain why.
6.  **Calculate AIC and BIC:**  Using the script or your own code, calculate the AIC and BIC values for both models.
7. **Compare and Discuss:**  Compare the likelihood ratio, AIC, and BIC values.  Discuss which model is most supported by the data. [INSTRUCTOR: Lead a brief class discussion on the limitations of each metric.]

**6. Data Collection (Table Template)**

| Parameter | Model 1 (Linear) | Model 2 (Quadratic) |
| :-------- | :--------------- | :------------------ |
|  Mean      |  [Value]        |   [Value]           |
|  Variance  |  [Value]        |    [Value]          |
|  Likelihood Ratio | [Value]          |   [Value]           |
|  AIC      | [Value]          |   [Value]           |
|  BIC     | [Value]          |   [Value]           |

**7. Analysis Questions (5 questions)**

1.  What does the likelihood ratio represent in the context of model comparison?
2.  Why might a model with more parameters have a lower likelihood ratio than a simpler model?
3.  How does the AIC and BIC relate to the likelihood ratio?
4.  In this scenario, which model is most likely to be the “best” according to the likelihood ratio test? Explain your reasoning.
5.  What are the limitations of relying solely on the likelihood ratio test for model selection?

**8. Expected Results (4 points)**

Students should observe that the likelihood ratio for Model 2 (quadratic) is greater than 1. The AIC and BIC values will also be affected by the increased complexity of Model 2. It is expected that the linear model will have a lower AIC and BIC value, suggesting it is the more parsimonious model. Students will learn that the likelihood ratio test is a formal way to compare models, however, other metrics such as AIC and BIC are often used in practice. [INSTRUCTOR:  Discuss the importance of considering both statistical evidence and model complexity when making model selection decisions.]