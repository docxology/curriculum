# Applications: AI & Robotics - Laboratory Exercise 17

## Lab Focus: Generative Adversarial Networks

---

**Module: Applications: AI & Robotics**
**Lab Number: 17**
**Lab Focus: Generative Adversarial Networks**

**1. Brief Background (87 words)**

This laboratory builds upon our discussion of Active Inference and Predictive Coding.  Generative Adversarial Networks (GANs) can be seen as a computational instantiation of this process. A GAN consists of two networks – a Generator and a Discriminator – that compete against each other. The Generator attempts to create data (e.g., images) that resemble real data, while the Discriminator attempts to distinguish between the generated data and real data.  This adversarial process mirrors the predictive coding framework, where the agent (Generator) is constantly refining its internal model (representation) based on feedback (Discriminator’s judgment). This lab will explore generating simple shapes using a trained GAN.

**2. Lab Objectives (4 bullet points)**

*   **Implement:** A simplified GAN using a pre-trained model for generating simple geometric shapes.
*   **Evaluate:** The quality of the generated shapes based on visual inspection and quantitative metrics (e.g., pixel difference).
*   **Modify:** Input parameters (e.g., noise level) to observe their effect on the generated shapes.
*   **Compare:** The output of the GAN with a baseline - randomly generated data.

**3. Materials and Equipment**

*   **Computer Hardware:**  Desktop or Laptop (minimum 8GB RAM, Intel Core i5 or equivalent)
*   **Software:** Python 3.8+, TensorFlow or PyTorch (student choice)
*   **Pre-trained GAN Model:**  A simplified GAN model pre-trained on a dataset of basic shapes (circles, squares, triangles). [INSTRUCTOR: Specify exact model – e.g., “SimpleShapeGAN - Version 1.2”]
*   **Image Display:** Monitor with sufficient resolution (1920x1080 recommended).
*   **USB Drive:** For data backup.
*   **Notebook/Paper & Pen:** For recording observations.

**4. Safety Considerations (⚠️)**

*   ⚠️ **Eye Safety:**  Prolonged screen viewing can cause eye strain. Take 15-minute breaks every hour.
*   ⚠️ **Computer Hygiene:**  Maintain a clean workspace to prevent hardware damage.  Do not eat or drink near computer equipment.
*   ⚠️ **Software Updates:**  Ensure all software is running the latest compatible version to avoid compatibility issues and potential vulnerabilities.
*   ⚠️ **Data Backup:**  Regularly back up your work to avoid data loss. [INSTRUCTOR: Remind students of importance of data integrity and backups]

**5. Procedure (7 steps)**

1.  **Load the GAN:** Execute the provided Python script to load the pre-trained SimpleShapeGAN model. [INSTRUCTOR: Provide the specific Python script location and instructions.]
2.  **Generate Shapes:** Use the script to generate 20 shapes.  Set the noise level to a default of 0.1.  Record the generated shapes in the output area.
3.  **Parameter Adjustment (Iteration 1):** Modify the noise level to 0.2. Generate 20 shapes and record the results.
4.  **Parameter Adjustment (Iteration 2):**  Change the noise level to 0.05. Generate 20 shapes and record the results.
5.  **Visual Inspection:** Examine the generated shapes closely, noting their similarity to original shapes, and any distortions.  Take screenshots of representative examples.
6.  **Data Recording:** Populate the "Data Collection Table" with observations from steps 5 and 6.
7.  **Repeat:** Repeat steps 5-7 for a total of 5 different noise levels (0.05, 0.1, 0.2, 0.3, 0.4)

**6. Data Collection (Table Template)**

| Noise Level | Shape 1 (Screenshot) | Shape 2 (Screenshot) | Shape 3 (Screenshot) | Shape 4 (Screenshot) | Shape 5 (Screenshot) | Qualitative Observations (e.g., sharpness, distortions, resemblance to original shapes) |
| :---------- | :------------------ | :------------------ | :------------------ | :------------------ | :------------------ | :-------------------------------------------------------------------- |
| 0.05        |                     |                     |                     |                     |                     |                                                                       |
| 0.1         |                     |                     |                     |                     |                     |                                                                       |
| 0.2         |                     |                     |                     |                     |                     |                                                                       |
| 0.3         |                     |                     |                     |                     |                     |                                                                       |
| 0.4         |                     |                     |                     |                     |                     |                                                                       |

**7. Analysis Questions (5 bullet points)**

*   How does the noise level affect the quality of the generated shapes?  Explain this relationship using the concepts of Active Inference and Predictive Coding.
*   What is the role of the Discriminator in this GAN?  How does its feedback drive the Generator’s learning process?
*   Compare the generated shapes to the original shapes.  What are the limitations of this simple GAN?
*   Consider how a more complex GAN (e.g., one trained on realistic images) might achieve a higher degree of realism.  How would this change the core principles of Active Inference?
*   How does this lab exercise illustrate the iterative nature of model building – a key aspect of the predictive coding framework?

**8. Expected Results (3 points)**

*   Students should observe that as the noise level increases, the generated shapes become more distorted and less resemble the original shapes. This demonstrates the Generator's struggle to accurately model the underlying distribution of the data.
*   The changes in shape quality as the noise level is varied will highlight the impact of uncertainty on the predictive coding process.
*   The students will realize that the GAN is an approximation model – it's attempting to *predict* the underlying data distribution, but it's inherently limited by its architecture and training data.