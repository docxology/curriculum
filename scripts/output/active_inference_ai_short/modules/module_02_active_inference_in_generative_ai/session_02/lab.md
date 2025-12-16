# Active Inference in Generative AI - Laboratory Exercise 2

## Lab Focus: Precision Weighting

---

**Module: 2 – Active Inference in Generative AI**
**Lab Number: 2**
**Lab Focus: Precision Weighting**

**1. Brief Background (98 words)**

Following our discussion on Active Inference and the core principles of predictive coding, this lab explores the role of precision weighting within Large Language Models.  The attention mechanism, at the heart of LLMs, directly implements predictive coding by constantly generating hypotheses about the next word in a sequence. However, not all predictions are created equal. Precision weighting allows the model to adjust its confidence in those predictions, reflecting the brain’s tendency to prioritize information that reduces prediction error most effectively. This lab will investigate how adjusting precision weighting impacts the LLM's output, providing a tangible demonstration of the active inference process. [INSTRUCTOR: Briefly demonstrate the concept of prediction error with a simple example – e.g., predicting a sunny day and it raining].

**2. Lab Objectives (4 bullet points)**

*   **Manipulate** the precision weighting parameter within a simplified LLM simulation.
*   **Analyze** the generated text output for variations in coherence and relevance based on different precision weighting settings.
*   **Document** observed changes in the generated text, specifically focusing on word choice and sentence structure.
*   **Relate** these observations to the concept of precision weighting as a mechanism for minimizing prediction error.

**3. Materials and Equipment**

*   **Computer:**  Laptop or desktop with Python 3.9+ installed.
*   **Software:**  Jupyter Notebook environment, pre-configured with the “Text Generation Simulation” code (provided - see Appendix A). This simulation mimics a simplified LLM.
*   **Simulation Parameters (Pre-configured):**
    *   Base Model: “SimpleGPT” (pre-trained on a small corpus of text)
    *   Initial Precision Weighting: 1.0
    *   Temperature: 0.7
*   **Data Collection Spreadsheet:** (Provided - see Appendix B)
*   **Calibration Tool:** Simple slider to adjust precision weighting.

**4. Safety Considerations (⚠️)**

*   **No Chemical Hazards:** This lab involves no hazardous materials.
*   **Computer Safety:**  Ensure proper ventilation. Do not operate equipment in wet conditions.
*   **Data Backup:**  Regularly save your work to prevent data loss. [INSTRUCTOR: Emphasize the importance of data management].
*   **Computational Resource Limits:** [INSTRUCTOR: Inform students that extended simulation runs may utilize significant computational resources.]

**5. Procedure (6 steps)**

1.  **Launch Simulation:** Open the “Text Generation Simulation” Jupyter Notebook.
2.  **Set Initial Parameter:** The default precision weighting is set to 1.0. Note this value in the data collection spreadsheet.
3.  **Generate Text:** Input the prompt “The quick brown fox” into the simulation.  Generate 50 words of text. Record the generated text in the data collection spreadsheet.
4.  **Adjust Precision Weighting:** Using the calibration slider, *decrease* the precision weighting to 0.5. Generate another 50 words of text using the same prompt.
5.  **Repeat:**  Increase the precision weighting to 1.5. Generate a third set of 50 words using the same prompt.
6. **Record Data:** Complete the data collection spreadsheet with the precision weighting setting and the corresponding generated text.

**6. Data Collection (Template)**

| Precision Weighting | Generated Text (50 Words) | Observations (Coherence, Relevance, Word Choice) |
|---------------------|----------------------------|-------------------------------------------------|
| 1.0                 | [Student Input]              | [Student Input]                               |
| 0.5                 | [Student Input]              | [Student Input]                               |
| 1.5                 | [Student Input]              | [Student Input]                               |

**7. Analysis Questions (5 questions)**

1.  How did the coherence and relevance of the generated text change as the precision weighting decreased?
2.  Describe the types of word choices you observed when the precision weighting was at 0.5 compared to 1.0.
3.  Explain how reducing precision weighting might reflect a simplified model of the brain’s active inference process.
4.  What role do you think precision weighting plays in preventing the model from “hallucinating” or generating nonsensical content?
5.  How might increasing the temperature parameter alongside precision weighting affect the results? [INSTRUCTOR: Introduce this as a follow-up discussion point]

**8. Expected Results (3 points)**

Students should observe that:

*   At 1.0, the generated text is generally coherent and relevant, but may contain minor inconsistencies.
*   At 0.5, the text becomes less coherent and more prone to illogical sequences, with more frequent instances of irrelevant or nonsensical words.
*   The lower precision weighting demonstrates how a reduced focus on minimizing prediction error can lead to a less accurate and more unstable model. [INSTRUCTOR: Encourage students to explain *why* this happens in terms of the active inference framework].