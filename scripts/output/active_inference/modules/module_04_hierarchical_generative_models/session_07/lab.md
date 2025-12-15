# Hierarchical Generative Models - Laboratory Exercise 7

## Lab Focus: Autoencoders

---

**Module: Hierarchical Generative Models – Lab 7: Autoencoders**

**Lab Number:** 7
**Lab Focus:** Autoencoders

**1. Brief Background (98 words)**

Following our discussion on Deep Predictive Processing and hierarchical generative models, this lab introduces Autoencoders – a core component in building these systems. Autoencoders are neural networks trained to reconstruct their input. The key concept is an ‘encoding’ phase where the input is compressed into a lower-dimensional representation (the ‘latent space’), followed by a ‘decoding’ phase that attempts to recreate the original input.  This process forces the network to learn the most important features of the data, mimicking the hierarchical abstraction observed in biological systems.  We will explore a simple convolutional autoencoder to illustrate this principle. [INSTRUCTOR: Briefly demonstrate a visual representation of an autoencoder architecture.]

**2. Lab Objectives (4 bullet points)**

*   Implement a simple convolutional autoencoder using [SPECIFIC FRAMEWORK - e.g., TensorFlow/Keras].
*   Train the autoencoder on a provided dataset of [SPECIFIC DATASET - e.g., MNIST handwritten digits].
*   Visualize the reconstructed images to assess the autoencoder’s performance.
*   Analyze the effects of varying the latent space dimension.

**3. Materials and Equipment**

*   **Hardware:**
    *   Laptop (minimum specifications: Intel i5 processor, 8 GB RAM, NVIDIA GTX 1050 or equivalent)
    *   [SPECIFIC SOFTWARE - e.g., Anaconda distribution with Python 3.8]
*   **Software:**
    *   [SPECIFIC FRAMEWORK - e.g., TensorFlow/Keras] – Version [SPECIFIC VERSION - e.g., 2.8.0]
    *   [SPECIFIC DATASET - e.g., MNIST dataset (downloaded from Keras)](https://keras.io/datasets/)
*   **Data:**
    *   Pre-loaded MNIST dataset (60,000 training images, 10,000 test images)
*   **Other:**
    *   USB Drive (for data transfer)

**4. Safety Considerations (⚠️)**

*   **Electrical Safety:** Ensure all electrical connections are secure. Avoid using damaged power cords.
*   **Computer Hygiene:** Regularly clean the laptop keyboard and screen with appropriate cleaning solutions. [INSTRUCTOR: Demonstrate proper cleaning techniques.]
*   **Data Security:** Do not share the dataset with unauthorized individuals.
*   **Eye Strain:** Take frequent breaks (every 20 minutes) to reduce eye strain. [INSTRUCTOR: Remind students to adjust screen brightness.]

**5. Procedure (7 steps)**

1.  **Setup Environment:** Launch the [SPECIFIC FRAMEWORK - e.g., TensorFlow/Keras] environment and install necessary packages.
2.  **Load Dataset:** Load the pre-loaded MNIST dataset into a NumPy array.
3.  **Build Autoencoder:** Construct a convolutional autoencoder model with a convolutional encoder and a convolutional decoder.  Specify the number of layers and filter sizes – e.g., 2 convolutional layers each with 32 filters of size 3x3, ReLU activation, and max-pooling with a pool size of 2x2.
4.  **Compile Model:** Compile the autoencoder using the Adam optimizer, binary cross-entropy loss function, and monitor the accuracy.
5.  **Train Model:** Train the autoencoder for [NUMBER - e.g., 20] epochs with a batch size of [NUMBER - e.g., 32].
6.  **Reconstruct Images:** After training, use the trained autoencoder to reconstruct the MNIST images from the test set.
7.  **Visualize Results:** Display a grid of original MNIST images alongside the reconstructed images to visually assess the autoencoder’s performance.

**6. Data Collection (Table Template)**

| Image Index | Original Image (Example - Display a sample image here) | Reconstructed Image (Example - Display a sample image here) | Reconstruction Error (e.g., Mean Squared Error) | Qualitative Assessment (e.g., Sharpness, Artifacts) |
| :---------- | :----------------------------------------------- | :-------------------------------------------------- | :----------------------------------------------- | :--------------------------------------------- |
| 1          | [INSERT IMAGE]                                   | [INSERT IMAGE]                                      | [VALUE - e.g., 0.05]                             | [TEXT - e.g., Some blurring]                       |
| 2          | [INSERT IMAGE]                                   | [INSERT IMAGE]                                      | [VALUE - e.g., 0.08]                             | [TEXT - e.g., Few artifacts]                     |
| ...         | ...                                             | ...                                                  | ...                                               | ...                                             |

**7. Analysis Questions (4 questions)**

1.  How does the size of the latent space (the number of neurons in the latent layer) affect the reconstruction quality?  Explain your observations based on your data.
2.  What types of images were most easily reconstructed by the autoencoder?  What about those that were more difficult?
3.  Describe the visual characteristics of the reconstructed images. What artifacts, if any, are present?  How do these relate to the concept of hierarchical representation?
4.  How does this lab exercise demonstrate the core principles of deep predictive processing and hierarchical generative models?

**8. Expected Results (2 paragraphs)**

Students should observe that as the latent space dimension decreases, the reconstruction quality generally improves, although there may be some loss of detail.  The autoencoder will attempt to capture the most salient features of the MNIST dataset, resulting in visually recognizable representations of the digits.  However, lower dimensions will inevitably lead to more noticeable compression artifacts – blurring, loss of fine detail, and potential misinterpretations of the digits.  The results will visually illustrate the trade-off between compression and reconstruction fidelity, mirroring the complexity found in hierarchical systems.  [INSTRUCTOR: Observe student reconstructions and provide targeted feedback.]