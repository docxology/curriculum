# Precision Weighting & Attention - Laboratory Exercise 8

## Lab Focus: Learning Precision Weights

---

**Module: Precision Weighting & Attention - Lab 8**
**Lab Number: 8**
**Lab Focus: Learning Precision Weights**

**1. Brief Background (98 words)**

This lab builds on the concepts introduced in Lecture 8 concerning dynamic priors and information gain. You’ve learned that our initial beliefs about a variable (the prior) are iteratively adjusted based on the data we receive. This adjustment is driven by information gain – the reduction in uncertainty associated with observing a new data point.  The core principle is that inaccurate initial priors are refined by data. In this exercise, you will directly manipulate the information gain to observe its impact on the ‘precision weighting’ of a simulated variable, reinforcing the link between prior beliefs and refined estimates. The goal is to understand how quickly and effectively precision weighting adapts to changing information.

**2. Lab Objectives (4 bullet points)**

*   **Observe:** How the ‘precision weighting’ of a variable changes as information gain increases.
*   **Manipulate:**  The amount of information gain applied to a simulated data input.
*   **Record:** Precise changes in the weighting value as data points are presented.
*   **Analyze:**  The impact of varying information gain on the evolving precision weighting.

**3. Materials and Equipment**

*   **Computer:** One per group of 2-3 students. Pre-installed with spreadsheet software (e.g., Microsoft Excel, Google Sheets).
*   **Spreadsheet Software:** (e.g., Microsoft Excel, Google Sheets).
*   **Data Input Sheet:** A pre-formatted Excel spreadsheet with columns labeled: “Iteration”, “Initial Weight”, “New Data Point”, “Information Gain”, “New Weight”, “Precision Weighting”.
*   **Data Point Values:** Set of 10 pre-defined values (e.g., 0, 1, 2, 3, 4, 5, 6, 7, 8, 9) – these will be your “new data points”.
*   **Instruction Manual:** Printed sheet outlining the complete procedure.

**4. Safety Considerations (⚠️)**

*   **Computer Safety:** Ensure all computer equipment is used on a stable surface. Avoid spilling liquids on any electronic devices.
*   **Eye Protection:**  [INSTRUCTOR] – Students *must* wear safety glasses at all times during the experiment. Failure to do so will result in immediate cessation of the lab and a reassessment. (⚠️ **Hazard: Potential eye injury from splashes or debris.**)
*   **General Computer Hygiene:** [INSTRUCTOR] –  Students must maintain a tidy workspace to prevent accidental damage to equipment.

**5. Procedure (7 steps)**

1.  **Initialization:** Open the “Data Input Sheet”.  Set the “Initial Weight” to 0.5 in cell A2.
2.  **Iteration Setup:** In column A, enter the iteration number from 1 to 10.
3.  **Data Input:** In cell A2, enter the first ‘New Data Point’ (e.g., 1).
4.  **Information Gain Calculation:** In cell B2, enter the ‘Information Gain’ (e.g., 0.2). This represents the magnitude of change in the weight based on the new data point.
5.  **Weight Update:** In cell C2, calculate the ‘New Weight’ by applying the information gain to the initial weight:  `New Weight = Initial Weight + Information Gain` (e.g., 0.5 + 0.2 = 0.7).
6.  **Repeat:**  Repeat steps 3-6 for each iteration, changing the ‘New Data Point’ to the next value in the set (0, 1, 2…9) and adjusting the ‘Information Gain’ (e.g., 0.2, 0.4, 0.6, 0.8, etc.).
7.  **Data Recording:**  Record all values in the corresponding cells of the spreadsheet.

**6. Data Collection (Table Template)**

| Iteration | Initial Weight | New Data Point | Information Gain | New Weight | Precision Weighting |
| :-------- | :------------- | :------------- | :--------------- | :--------- | :------------------- |
| 1         | 0.5            | 1              | 0.2              |            |                      |
| 2         |                |                |                  |            |                      |
| 3         |                |                |                  |            |                      |
| 4         |                |                |                  |            |                      |
| 5         |                |                |                  |            |                      |
| 6         |                |                |                  |            |                      |
| 7         |                |                |                  |            |                      |
| 8         |                |                |                  |            |                      |
| 9         |                |                |                  |            |                      |
| 10        |                |                |                  |            |                      |

**7. Analysis Questions (5 questions)**

1.  How does the “Precision Weighting” change as the ‘Information Gain’ increases from 0.2 to 0.8? Provide specific examples of changes you observe in the spreadsheet.
2.  What happens to the “Precision Weighting” when the ‘Information Gain’ is very low (e.g., 0.1)? Explain your observations.
3.  What is the relationship between ‘Information Gain’ and the speed with which the ‘Precision Weighting’ adapts to new data?
4.  Consider a scenario where the ‘New Data Point’ consistently remains at the same value throughout the iterations.  How would this impact the ‘Precision Weighting’?
5.  If the initial ‘Precision Weight’ was 0.8, what would be the expected change in precision weighting after 10 iterations with a constant information gain of 0.3?

**8. Expected Results (Observations & Rationale)**

Students should observe that the “Precision Weighting” initially increases rapidly as the ‘Information Gain’ is high.  As the ‘Information Gain’ decreases, the rate of change slows down. After the first few iterations, the precision weighting will tend to stabilize, approaching the value determined by the final information gain. This demonstrates the iterative nature of dynamic priors and how they converge to a more accurate representation of the variable's relevance. The initial rapid change reflects immediate adjustments, while the subsequent stabilization indicates the system is settling on a refined estimate.