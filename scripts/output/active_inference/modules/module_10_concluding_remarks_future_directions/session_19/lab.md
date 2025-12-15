# Concluding Remarks & Future Directions - Laboratory Exercise 19

## Lab Focus: Uncertainty & Noise

---

**Lab Number: 19**
**Lab Focus: Uncertainty & Noise**

**1. Brief Background (98 words)**

Following our lecture discussion on Bayesian modeling and the inherent challenges of quantifying uncertainty, this lab explores how noise impacts model estimates and the representation of that noise within a Bayesian framework. We will investigate a simplified scenario mimicking the challenge of estimating a true signal within a noisy environment. The underlying principle remains that all models are simplifications, and capturing random variation – aleatoric uncertainty – is crucial. This exercise will provide hands-on experience with simulating this noise and evaluating the impact on our ability to infer the true value of a parameter. [INSTRUCTOR] Note: This lab intentionally avoids complex data analysis, focusing on conceptual understanding.

**2. Lab Objectives (4 bullet points)**

*   Simulate a system generating random data with added noise.
*   Construct a Bayesian model to estimate the true signal from the noisy data.
*   Assess the impact of varying the noise level on the model’s predictive performance.
*   Critically evaluate the choice of prior distribution based on the available information.

**3. Materials and Equipment**

*   **Data Generation:**
    *   Computer with Statistical Software (R or Python recommended) – 1 computer
    *   Noise Generator Software (e.g., built-in functions in R/Python) – Provided by [INSTRUCTOR]
    *   Signal Generator – Provided by [INSTRUCTOR]
*   **Measurement & Observation:**
    *   Digital Voltmeter - 1 unit
    *   Oscilloscope (Optional - for visualization of signal) – 1 unit
    *   Ruler or Measuring Tape – 1 unit
*   **Consumables:**
    *   Connecting Wires – 10 meters

**4. Safety Considerations (⚠️)**

*   **Electrical Safety:**  Handle all electrical equipment with care. Avoid contact with water. Ensure proper grounding. **⚠️ WARNING:**  Do not operate equipment near flammable materials.
*   **Equipment Handling:**  Handle all equipment gently to prevent damage.  Report any damaged equipment to [INSTRUCTOR] immediately.
*   **Data Integrity:**  Do not alter or modify the provided software or data sets without [INSTRUCTOR]’s approval.
*   **Time-Sensitive Step:**  Allow 30 seconds between the start of the signal generation and the measurement phase to ensure stable data acquisition.

**5. Procedure (7 steps)**

1.  **Signal Generation:** Using the provided software, generate a sinusoidal signal with a frequency of 1 Hz and an amplitude of 1 volt.  Record the true signal value in the data table.
2.  **Noise Addition:** Introduce random noise to the signal. Vary the noise level (standard deviation) from 0.1 volts to 2.0 volts in increments of 0.5 volts. For each noise level, record the noisy data.
3.  **Data Acquisition:** For each noise level, use the voltmeter to measure the amplitude of the noisy signal. Record the measured amplitude in the data table.
4.  **Model Construction (Conceptual):**  Assume a Bayesian model where the measured amplitude is a noisy observation of the true signal.  Consider a Gaussian prior for the signal amplitude and a Gaussian likelihood for the noisy data. (No actual model coding is required, focus on conceptual understanding).
5.  **Repeat:** Repeat steps 3 and 4 for each noise level.
6.  **Data Table Completion:** Record all data in the provided data table.

**6. Data Collection**

| Noise Level (Standard Deviation, Volts) | True Signal Amplitude (Volts) | Measured Amplitude (Volts) |
| --------------------------------------- | ----------------------------- | -------------------------- |
| 0.1                                     |                              |                          |
| 0.5                                     |                              |                          |
| 1.0                                    |                              |                          |
| 1.5                                    |                              |                          |
| 2.0                                    |                              |                          |

**7. Analysis Questions (5 questions)**

1.  How does increasing the noise level affect the accuracy of your measured amplitude estimates?
2.  What role does the prior distribution play in the Bayesian inference process? How might different priors influence the final estimates?
3.  Explain the concept of aleatoric uncertainty and how it relates to the noise in this experiment.
4.  If the true signal were known, what type of error would the measured amplitude represent?
5.  How might this experiment be adapted to investigate the impact of different types of noise (e.g., Gaussian, uniform, impulse) on model performance?

**8. Expected Results (70 words)**

Students should observe that as the noise level increases, the measured amplitude estimates deviate more significantly from the true signal amplitude.  The use of a prior distribution will shape the posterior distribution, potentially reflecting prior knowledge about the signal. The exercise highlights the fundamental challenge of model construction when dealing with inherent uncertainty and the influence of noise on inference.