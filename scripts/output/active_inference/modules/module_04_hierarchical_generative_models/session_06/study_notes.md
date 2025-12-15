# Hierarchical Generative Models - Study Notes

## Key Concepts

## Hierarchical Generative Models: Study Notes

**Concept Name**: Hierarchical Prediction: Hierarchical prediction refers to the process where a system—such as the brain or a generative model—makes predictions at multiple levels of abstraction. Lower-level units predict the activity of higher-level units, and these predictions are then refined through error signals. This creates a nested structure of prediction and correction, allowing for the modeling of complex, time-varying phenomena.

**Concept Name**: Prediction Error: Prediction error represents the difference between a predicted value and the actual observed value. It’s the core signal driving learning and adaptation within predictive processing frameworks.  A large prediction error indicates a poor prediction, prompting the system to adjust its internal model, while a small error suggests a good fit.

**Concept Name**: Recurrent Connections: Recurrent connections are connections within a neural network where the output of a unit is fed back into itself or another unit within the same network. This creates a feedback loop, enabling the network to maintain a “memory” of past states and temporal dependencies. Think of it like an echo – the signal bounces back, reinforcing itself.

**Concept Name**: Precision Weighting: Precision weighting is a mechanism used to adjust the influence of different predictions based on their associated prediction errors.  Units with larger prediction errors receive a stronger influence, effectively amplifying their contribution to the overall prediction. This allows the system to focus on the most informative elements of its internal model.  It’s like giving more attention to the most challenging predictions.

**Additional Points & Concepts**

*   **Temporal Dependencies**: Recurrent connections are essential for modeling temporal dependencies – the relationships between events that occur over time.  This is fundamental to understanding many real-world phenomena, from weather patterns to speech recognition.
*   **Error Minimization**: The overarching goal of predictive processing is to minimize prediction error over time. This process drives adaptation and learning within the system.
*   **Layered Models**: Hierarchical models are typically organized into layers, with each layer responsible for predicting the activity of the next layer.
*   **Bayesian Framework**: Predictive processing is often framed within a Bayesian framework, where the system updates its beliefs about the world based on incoming sensory evidence and its own predictions.

**Mnemonics/Memory Aids**

*   **Hierarchical Prediction**: “Hierarchical” sounds like “high order,” reflecting the multiple levels of the model.
*   **Precision Weighting**: “Precision” emphasizes the importance of accurate prediction.