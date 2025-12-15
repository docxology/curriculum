# Bayesian Mechanics - Laboratory Exercise 3

## Lab Focus: Prior, Likelihood, Posterior

---

**Module: Bayesian Mechanics – Lab 3: Prior, Likelihood, Posterior**

**Lab Number:** 3
**Lab Focus:** Prior, Likelihood, Posterior

**Related Topics:** Prior, Likelihood, Posterior

**1. Brief Background (98 words):**

This laboratory exercise builds upon the principles of Bayesian mechanics introduced in the previous lecture. We will explore how prior beliefs about a system's parameters influence our understanding of that system when combined with observed data. Specifically, we will analyze the lifespan of a simulated machine, initially assuming a lifespan of 5 years (our prior). However, a simulated failure event will introduce new data, forcing us to update our belief using Bayes’ Theorem to calculate the posterior distribution for the machine’s lifespan. This exercise emphasizes the iterative nature of Bayesian inference and the crucial role of both prior knowledge and observed data.  [INSTRUCTOR: Ensure students understand the concept of a ‘prior’ as an initial belief.]

**2. Lab Objectives (4 bullet points):**

*   Calculate the prior probability distribution for the machine's lifespan.
*   Determine the likelihood of observing data related to a machine failure.
*   Compute the posterior probability distribution for the machine's lifespan after observing a failure event.
*   Apply Bayes’ Theorem to update a prior belief based on observed data.

**3. Materials and Equipment:**

*   **Data Simulation Software:** “MachineLifeSim” (Version 1.2) – pre-installed on computers. (Software documentation available separately).
*   **Computer:** Running MachineLifeSim.
*   **Calculators:** Scientific calculators with statistical functions.
*   **Data Analysis Spreadsheet:** Microsoft Excel or Google Sheets.
*   **Graph Paper:** For sketching probability distributions.
*   **Ruler:** For accurate plotting.

**4. Safety Considerations (⚠️):**

*   **Computer Equipment:** Avoid spilling liquids on computers.  Do not operate computer equipment near water sources.  Immediately report any hardware malfunctions to [INSTRUCTOR].
*   **Data Security:**  Do not share simulation data or software configurations.
*   **Eye Protection:** Goggles must be worn at all times during computer operation. ⚠️ (Risk of potential electrical shock – low probability but present).
*   **Software Usage:** Follow all software instructions carefully.  Do not attempt to modify the simulation code without explicit permission from [INSTRUCTOR].

**5. Procedure (6 steps):**

1.  **Initialize Simulation:** Launch MachineLifeSim. Set the prior probability distribution for machine lifespan to a uniform distribution between 3 and 7 years, with a peak at 5 years. Set the simulation to run for 1000 trials.
2.  **Run Simulation:** Initiate the simulation. The software will generate 1000 simulated machine lifespans.
3.  **Observe Data:**  Record the number of simulated machines that failed (stopped working) during the 1000 trials. This will be your observed data.
4.  **Calculate Likelihood:**  Using the observed failure data, determine the likelihood function, P(Failure Data | Lifespan). [INSTRUCTOR: Guide students to understand that this is the probability of observing the given failure rate if a specific lifespan exists.]
5.  **Calculate Posterior:** Using Bayes' Theorem, calculate the posterior distribution for the machine’s lifespan,  P(Lifespan | Failure Data). [INSTRUCTOR: Provide a template for the Bayesian calculation – ensure students use the correct formula.]
6.  **Analyze Distribution:** Sketch the posterior probability distribution based on your calculated values.  Compare it to the prior distribution.  [INSTRUCTOR: Discuss the shift in the distribution after observing the failure.]

**6. Data Collection:**

| Parameter             | Value | Units |
| --------------------- | ----- | ----- |
| Prior Lifespan Peak | 5     | Years |
| Prior Lifespan Spread | 2     | Years |
| Number of Failures    | [DATA] | Trials |
| Posterior Lifespan Peak | [DATA] | Years |
| Posterior Lifespan Spread | [DATA] | Years |

**7. Analysis Questions (4 bullet points):**

*   How did the observed failure data influence the posterior distribution compared to the prior?
*   Explain how Bayes’ Theorem integrates prior knowledge with new evidence to produce the posterior distribution.
*   If the number of failures was significantly higher (e.g., 800 failures out of 1000), how would this affect the posterior distribution?
*   Describe the relationship between the likelihood function and the posterior distribution.

**8. Expected Results (3 points):**

Students should observe that the posterior distribution shifts towards shorter lifespans compared to the prior, reflecting the increased probability of a failure event. The spread of the posterior distribution will also be narrower than the prior, indicating greater certainty about the machine's lifespan after observing the failure. [INSTRUCTOR:  Demonstrate how the software generates the posterior distribution graphically.] The observed change validates the application of Bayesian inference for updating beliefs in the face of new data.