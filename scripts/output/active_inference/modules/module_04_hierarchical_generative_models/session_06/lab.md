# Hierarchical Generative Models - Laboratory Exercise 6

## Lab Focus: Prediction Error

---

**Module: Hierarchical Generative Models – Lab 6: Prediction Error**

**Lab Number:** 6
**Lab Focus:** Prediction Error

**1. Brief Background:**

This lab builds upon the concepts of hierarchical generative models and recurrent predictive models.  We’ve established that these systems utilize hierarchical prediction – lower levels predicting higher levels – with prediction errors driving adjustments. This lab explores how recurrent connections introduce a temporal memory component, allowing the model to incorporate past states into its current predictions. The core principle is that a model's accuracy improves as it incorporates more historical information through feedback loops, mimicking how the brain processes sensory input over time. [INSTRUCTOR: Briefly demonstrate a simple diagram of a recurrent model].

**2. Lab Objectives:**

*   Construct a simple recurrent predictive model using a provided software environment.
*   Generate a time series data sequence using the model, observing how the model's predictions evolve over time.
*   Analyze the model's output, specifically focusing on the magnitude and persistence of prediction errors.
*   Identify how changes in the recurrent connections influence the model’s ability to predict future states.
*   Compare the model's performance with a static prediction model (if implemented).

**3. Materials and Equipment:**

*   **Software:** Python environment with NumPy, SciPy, and Matplotlib libraries installed.  (Version 3.9 or higher recommended).
*   **Hardware:** Laptop or desktop computer with sufficient processing power (minimum 8GB RAM).
*   **Provided Code:** `recurrent_model.py` (includes initial model architecture and training loop). This file will be provided to the students.
*   **Data Generation Parameters:** Initial state value (e.g., 1.0), learning rate (e.g., 0.1), recurrent connection strength (e.g., 0.8), and sequence length (e.g., 100 steps).
*   **Calibration Tool:** Multimeter (for verifying power supply – see safety section).

**4. Safety Considerations:**

⚠️ **Electrical Safety:** This lab involves working with a small DC power supply.  Incorrect use could result in electric shock or equipment damage.
⚠️ **Eye Protection:** Always wear safety goggles throughout the experiment to protect your eyes from potential splashes or flying debris.
⚠️ **Electrical Shock Hazard:** Ensure the power supply is properly connected and the cable is in good condition. Do not use the power supply if the cable is damaged. [INSTRUCTOR:  Demonstrate proper power supply connection and disconnection].
⚠️ **Static Electricity:**  Ground yourself frequently by touching a metal object before handling the power supply.
⚠️ **Material Handling:** Dispose of any generated waste appropriately, following local regulations.

PPE Requirements: Safety goggles, lab coat, rubber gloves.

**5. Procedure:**

1.  **Setup:** Open the `recurrent_model.py` file in your Python environment. Ensure all necessary libraries are installed.
2.  **Parameter Configuration:** Modify the following parameters within the script: `initial_state`, `learning_rate`, and `recurrent_connection_strength`. Record the chosen values in the Data Collection table.
3.  **Model Initialization:** Run the script. The model will initialize with the specified parameters.
4.  **Data Generation:**  The model will generate a time series data sequence. Observe the output displayed in the console window.
5.  **Parameter Variation:**  Change the `recurrent_connection_strength` to values of 0.5, 0.9, and 1.0.  For each change, run the model and observe the resulting data sequence. Record the observed changes in the Data Collection table.
6.  **Sequence Length Adjustment:**  Change the `sequence_length` from 50 to 100 and repeat steps 5.

**6. Data Collection:**

| Parameter          | Value     | Observation                               |
| ------------------ | --------- | ---------------------------------------- |
| Initial State       | 1.0       |                                          |
| Learning Rate       | 0.1       |                                          |
| Recurrent Connection Strength | 0.8       | Qualitative description of output behavior |
| Sequence Length     | 100       |                                          |
| Recurrent Connection Strength | 0.5       |                                          |
| Recurrent Connection Strength | 0.9       |                                          |
| Recurrent Connection Strength | 1.0       |                                          |

**7. Analysis Questions:**

1.  How does increasing the `recurrent connection_strength` affect the persistence of the prediction errors?
2.  Describe the relationship between the `learning rate` and the stability of the model’s output.
3.  Predict how the model’s output would change if the recurrent connections were completely absent (recurrent_connection_strength = 0).
4.  Explain how the concept of prediction error drives the learning process in a recurrent predictive model.
5.  Considering the limitations of this simple model, what factors might contribute to a more accurate prediction in a real-world scenario?

**8. Expected Results:**

Students should observe that as the `recurrent connection_strength` increases, the model’s predictions become more stable and less prone to erratic fluctuations.  The prediction errors will generally decrease in magnitude and exhibit a longer duration.  Changes in the learning rate will influence the convergence speed and, potentially, the stability of the solution.  A complete absence of recurrent connections (recurrent_connection_strength = 0) will result in a highly volatile and unpredictable output. The overall goal is to demonstrate that incorporating historical information through feedback loops significantly improves the model's predictive ability. [INSTRUCTOR:  Expected range for initial error: 0.1 – 0.3].