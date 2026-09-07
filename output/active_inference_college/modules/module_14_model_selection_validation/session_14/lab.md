# Model Selection & Validation - Laboratory Exercise 14

## Lab Focus: Hold-out Sets

---

**Module: Model Selection & Validation**
**Lab Number: 14**
**Lab Focus: Hold-out Sets**

**1. Brief Background (87 words)**

Following our discussion on overfitting and the limitations of single hold-out sets, this laboratory exercise focuses on reinforcing your understanding of how a hold-out set is used to assess model performance. You will implement a basic hold-out set approach to evaluate a simple linear regression model. This practical application highlights the importance of considering data distribution and potential biases introduced by a limited hold-out sample. The goal is to demonstrate the potential for variance in performance estimates derived solely from a single hold-out set. [INSTRUCTOR: Monitor student understanding of the risk of skewed results from small hold-out sets.]

**2. Lab Objectives (4 bullet points)**

*   Create a simple linear regression model using a provided dataset.
*   Divide the dataset into a training set and a hold-out set.
*   Train the model on the training set.
*   Evaluate the model's performance on the hold-out set using Mean Squared Error (MSE).
*   Document your observations regarding the variability of performance estimates.

**3. Materials and Equipment**

*   **Software:** Microsoft Excel (or equivalent spreadsheet software)
*   **Data Set:** “HousePriceData.csv” – Contains house size (square feet) and selling price (USD). (File includes 100 records)
*   **Calculators:** [INSTRUCTOR: Ensure students have access to scientific calculators.]
*   **Computer with Internet Access:** For downloading required data and accessing documentation.

**4. Safety Considerations (⚠️)**

⚠️ **No hazardous materials are involved in this exercise.**
⚠️ **Physical Safety:** Students should maintain a clear workspace to prevent tripping hazards.  [INSTRUCTOR: Remind students to use computer equipment responsibly.]
⚠️ **Data Security:**  Do not share your data files with unauthorized individuals.
⚠️ **Time-Sensitive Step:** All calculations must be completed within a 60-minute timeframe to simulate a realistic data analysis scenario.

**5. Procedure (7 steps)**

1.  **Open Excel:** Launch Microsoft Excel.
2.  **Import Data:** Open the “HousePriceData.csv” file. Ensure data is correctly imported into the spreadsheet.
3.  **Split Data:**  Divide the dataset into two subsets: a training set (70% of the data - 70 records) and a hold-out set (30% of the data - 30 records).  Manually copy and paste or use Excel’s sorting/filtering to achieve this split.
4.  **Linear Regression:**  Using Excel’s “Data Analysis Toolpak” (add the toolpak if necessary), perform a simple linear regression analysis using “Square Feet” as the independent variable and “Price” as the dependent variable, utilizing *only* the training data.
5.  **Model Evaluation:**  Using the regression equation generated from the training data, predict the price for each house in the hold-out set.
6.  **Calculate MSE:** Calculate the Mean Squared Error (MSE) for the hold-out set, using the predicted prices and the actual selling prices.
7.  **Record Observations:**  Document your observations regarding the MSE value. [INSTRUCTOR: Prompt students to discuss potential reasons for variation in MSE.]

**6. Data Collection**

| House ID | Square Feet | Predicted Price | Actual Price | MSE Value (Hold-out Set) |
|---|---|---|---|---|
| 1 | 1200 |  |  |  |
| 2 | 1500 |  |  |  |
| ... (30 records) |  |  |  |  |
| **Total MSE Value** | | | | |

**7. Analysis Questions (5 questions)**

1.  What is the MSE value calculated for the hold-out set?  Interpret its meaning in the context of the model’s predictive performance.
2.  How does the MSE value compare to the MSE value you might expect if you were to build the model using the *entire* dataset?
3.  How might the size of the hold-out set influence the MSE value?
4.  Consider the "HousePriceData.csv" – what potential biases could be present in the dataset that might affect the MSE value?
5.  Explain how the concept of overfitting relates to the observed MSE values.

**8. Expected Results (70-100 words)**

Students should observe that the MSE value calculated for the hold-out set will likely vary slightly from the MSE value calculated if the entire dataset had been used. This variability demonstrates the inherent risk of relying solely on a single hold-out set. A larger variance in the MSE reflects the impact of a limited sample size on the model’s performance estimation. The exercise will highlight how a hold-out set provides a single, potentially misleading, performance measure. [INSTRUCTOR: Encourage students to discuss how increasing the size of the hold-out set could potentially reduce the variance in MSE.]