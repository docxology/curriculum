# Variational Free Energy – Definition & Interpretation - Laboratory Exercise 6

## Lab Focus: Relationship to Surprise

---

**Lab Number:** 6
**Lab Focus:** Relationship to Surprise

**1. Brief Background (98 words)**

This laboratory exercise builds upon the concepts introduced in the Variational Free Energy module. We will explore the core idea behind the VFE as a measure of “surprise” – quantifying the difference between a chosen approximate posterior distribution and the true, intractable posterior.  Using a simplified, simulated dataset, students will manually calculate the VFE, directly experiencing the concept of surprise. The goal is to understand how a discrepancy between predicted and observed data manifests as an increase in the VFE, illustrating the fundamental principle behind variational inference: approximating an intractable posterior with a tractable one. This practical exercise provides a tangible connection between the theoretical definition and the intuitive notion of mismatch.

**2. Lab Objectives (4 bullet points)**

*   Calculate the Variational Free Energy (VFE) for a given dataset and a chosen approximate posterior distribution.
*   Identify and quantify the "surprise" associated with deviations between predicted and observed data.
*   Compare the VFE for different approximate posterior distributions.
*   Understand the relationship between the VFE and the difference between predicted and observed values.

**3. Materials and Equipment**

*   **Dataset:** Simulated Weather Dataset (Attached – CSV file: “weather_data.csv”) – Contains temperature (Celsius) and humidity (%), 100 data points.
*   **Spreadsheet Software:** Microsoft Excel or Google Sheets.
*   **Calculator:** Scientific calculator with statistical functions.
*   **Pen & Paper:** For calculations and note-taking.
*   **Computer:** For dataset access and spreadsheet manipulation.

**4. Safety Considerations (⚠️)**

*   **No Hazardous Materials:** This experiment utilizes only digital data.
*   **Computer Hygiene:** Ensure workstation is clean to prevent equipment malfunction. Avoid spills.
*   **Data Security:** Protect your spreadsheet data; store the file securely.
*   **Eye Protection:** [INSTRUCTOR] – Strongly recommended when working with computer screens for extended periods.

**5. Procedure (7 steps)**

1.  **Data Loading:** Open the “weather_data.csv” file in your chosen spreadsheet software. Ensure the data is correctly imported (temperature in Celsius, humidity in %).
2.  **Define Approximate Posterior:** Assume a simple, Gaussian approximation posterior:  `p_θ(x) = N(μ, σ²)`, where θ represents the mean (μ) and variance (σ²) – initially set μ = 0 and σ² = 1.  Record these initial values.
3.  **Calculate Predicted Values:** Using μ = 0 and σ² = 1, predict the temperature and humidity for each data point in the dataset. These are your “predicted values”.
4.  **Calculate the Difference (Error):** For each data point, calculate the difference between the observed temperature and the predicted temperature.  Similarly, calculate the difference between the observed humidity and the predicted humidity.  These are your "errors".
5.  **Calculate the Squared Error:** Square each of the "errors" calculated in step 4.
6.  **Calculate the Mean Squared Error (MSE):** Calculate the average of the squared errors. This is a proxy for the VFE calculation.  Record this value.
7.  **Experiment with Variation:** Change the value of σ² (variance) in your spreadsheet. Recalculate the MSE. Observe how the value changes.

**6. Data Collection (Table Template)**

| Data Point | Observed Temperature (°C) | Observed Humidity (%) | Predicted Temperature (°C) | Predicted Humidity (%) | Error (Temperature) | Error (Humidity) | Squared Error (Temperature) | Squared Error (Humidity) |
| :--------- | :------------------------ | :--------------------- | :-------------------------- | :--------------------- | :------------------- | :------------------ | :-------------------------- | :------------------------- |
| 1          | [INSERT VALUE]            | [INSERT VALUE]         | [INSERT VALUE]              | [INSERT VALUE]         | [INSERT VALUE]       | [INSERT VALUE]      | [INSERT VALUE]              | [INSERT VALUE]            |
| 2          | [INSERT VALUE]            | [INSERT VALUE]         | [INSERT VALUE]              | [INSERT VALUE]         | [INSERT VALUE]       | [INSERT VALUE]      | [INSERT VALUE]              | [INSERT VALUE]            |
| …          | …                         | …                     | …                          | …                     | …                   | …                  | …                          | …                         |
| 100        | [INSERT VALUE]            | [INSERT VALUE]         | [INSERT VALUE]              | [INSERT VALUE]         | [INSERT VALUE]       | [INSERT VALUE]      | [INSERT VALUE]              | [INSERT VALUE]            |

**7. Analysis Questions (5 questions)**

1.  How does the value of the VFE (MSE) change when you increase the value of σ²? Explain your reasoning.
2.  What does a large value of the VFE (MSE) signify in the context of this experiment?
3.  Imagine you are trying to fit a more complex distribution to the weather data. How might a more complex distribution affect the VFE?
4.  What assumptions are being made by approximating the posterior with a Gaussian distribution?
5.  Explain how this laboratory exercise mirrors the core concept of variational inference.

**8. Expected Results (2 sentences)**

Students should observe that increasing σ² results in a lower VFE (smaller MSE). This is because a larger variance allows the distribution to accommodate more deviations between predicted and observed values, reducing the "surprise" – the term used to quantify the difference and, therefore, the VFE.