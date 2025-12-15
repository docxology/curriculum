# Model Learning & Structure Learning - Laboratory Exercise 13

## Lab Focus: Adding/Removing Connections

---

## Lab 13: Adding/Removing Connections – Dynamic Architecture

**Module:** Model Learning & Structure Learning
**Lab Number:** 13
**Lab Focus:** Adding/Removing Connections

---

**1. Brief Background (98 words)**

This laboratory exercise explores the concept of structure learning within machine learning, building upon the lecture’s discussion of parameter learning versus architecture design.  We’ll investigate techniques for dynamically modifying neural network architectures – specifically, adding and removing connections – to create hierarchical models.  The goal is to move beyond a fixed architecture and understand how the structure of a model influences its learning ability.  We will examine a simplified model with initial connections and intentionally modify its topology to observe the impact on performance. This activity directly addresses the challenges of adapting to complex, real-world data by allowing the model to evolve its structure during training, mirroring the evolutionary development of biological neural networks.

---

**2. Lab Objectives (4 bullet points)**

*   Construct a neural network model with a defined initial architecture.
*   Implement a procedure for adding connections between neurons.
*   Experiment with varying the number of added connections.
*   Analyze the impact of connection additions on the model's output.
*   Document the changes made to the model’s architecture and resulting performance.

---

**3. Materials and Equipment**

*   **Software:** Python 3.9+, TensorFlow/Keras
*   **Hardware:** Laptop with sufficient RAM (8GB minimum)
*   **Components:**
    *   Pre-built TensorFlow/Keras environment – Version 2.10.0 (or later)
    *   Sample Data: Synthetic dataset of 1000 data points, 2 input features, 1 output feature, created using the Python code provided [INSTRUCTOR - Link to Python script]. Data range: 0-1
    *   Breadboard
    *   Jumper Wires (Quantity: 20)
    *   LEDs (Quantity: 10, Various colors)
    *   Resistors (Quantity: 10, 220Ω)

---

**4. Safety Considerations (⚠️)**

*   **Electrical Safety:**  Low-voltage components are used.  Do not exceed the specified voltage limits (maximum 5V DC). Ensure all connections are secure to prevent short circuits.  [INSTRUCTOR - Note: Check all connections before applying power].
*   **Eye Protection:**  Wear safety glasses/goggles at all times during experimentation.  [INSTRUCTOR - Specifically, ANSI Z87.1 rated safety glasses required].
*   **Component Handling:** Handle electronic components with care. Avoid dropping or damaging them.
*   **Time Sensitive Step:**  When applying power, observe the circuit for no more than 60 seconds. Immediately disconnect power if smoke or unusual behavior is observed.

---

**5. Procedure (7 steps)**

1.  **Setup:** Connect the LEDs and resistors in series to form a simple circuit. Each LED and resistor combination represents a single node in the network.
2.  **Initial Network Construction:** Using TensorFlow/Keras, create a feedforward neural network with 3 input neurons, 2 hidden layers with 4 and 2 neurons respectively, and 1 output neuron.  The network should be initialized with random weights. [INSTRUCTOR - Provide Keras code snippet].
3.  **Connection Addition (Step 1):** Add one connection between the output of the second hidden layer and the output neuron. Use a ReLU activation function.
4.  **Connection Addition (Step 2):** Add another connection between the output of the first hidden layer and the output neuron. Use a ReLU activation function.
5.  **Training:** Train the network on the synthetic dataset for 100 epochs using a learning rate of 0.01. Monitor the loss and accuracy on a validation set.
6.  **Observation:** Record the loss and accuracy after each epoch. Observe changes in the output when changing the number of connections.
7.  **Documentation:**  Document all changes made to the network architecture, training parameters, and observed results in the data collection table.

---

**6. Data Collection**

| Epoch | Network Architecture | Number of Connections | Loss | Accuracy | Output Observation |
|---|---|---|---|---|---|
| 0 | 3 Input -> 4 Hidden -> 2 Hidden -> 1 Output | 3 | [Value] | [Value] | [Describe Observed Output] |
| 1 | 3 Input -> 4 Hidden -> 2 Hidden -> 1 Output | 3 | [Value] | [Value] | [Describe Observed Output] |
| 10 | 3 Input -> 4 Hidden -> 2 Hidden -> 1 Output | 3 | [Value] | [Value] | [Describe Observed Output] |
| 50 | 3 Input -> 4 Hidden -> 2 Hidden -> 1 Output | 3 | [Value] | [Value] | [Describe Observed Output] |
| 100 | 3 Input -> 4 Hidden -> 2 Hidden -> 1 Output | 3 | [Value] | [Value] | [Describe Observed Output] |

---

**7. Analysis Questions (4 Questions)**

1.  How did adding connections affect the network’s loss and accuracy over time? Explain your observations.
2.  What is the likely reason for the changes in performance when connections were added?
3.  How does this experiment relate to the concept of hierarchical models and their ability to represent complex data?
4.  What limitations does this simplified model have compared to a more sophisticated deep learning architecture?

---

**8. Expected Results (2 Statements)**

*   Students should observe a decrease in the loss and an increase in the accuracy as more connections are added initially, but the increase will plateau and eventually lead to overfitting if too many connections are added.
*   The added connections will allow the network to learn more complex patterns in the data, but excessive connections can lead to instability and reduced generalization performance.