# Precision Weighting & Attention - Study Notes

## Key Concepts

## Precision Weighting & Attention

**Introduction:** Precision Weighting & Attention explores how systems prioritize information, driven by a need to efficiently process overwhelming data. This session focuses on the core mechanism: free energy minimization.

**Key Concepts:**

**Free Energy Minimization**: Free Energy Minimization: The fundamental principle that all systems – from simple thermostats to complex brains – strive to minimize their “surprise” by constructing internal models that accurately predict sensory input. This isn’t direct control, but a predictive process.

**Sensory Input**: Sensory Input: The raw data received from the environment, such as visual, auditory, or tactile information. This serves as the primary driver for attention processes.

**Internal Model**: Internal Model: A representation of the world constructed by a system, allowing it to make predictions about future sensory input. This model is constantly updated based on incoming sensory data.

**Attention**: Attention: The selective focusing of cognitive resources on specific aspects of sensory information, enhancing processing of relevant stimuli and suppressing irrelevant ones. It's a key component of free energy minimization.

**Predictive Coding**: Predictive Coding: A hierarchical model of brain function where the brain constantly generates predictions about sensory input and updates its internal model based on the difference between predictions and actual sensory input (prediction error). Attention can be viewed as a mechanism for amplifying prediction errors.

**Bayesian Inference**: Bayesian Inference: A statistical method used to update beliefs about the world based on new evidence. In the context of attention, it suggests that the system actively seeks out information that best confirms its current beliefs while minimizing surprise.

**Prediction Error**: Prediction Error: The difference between a system’s prediction of sensory input and the actual sensory input received.  A large prediction error signals a significant change in the environment and often triggers attention.

**Contextual Relevance**: Contextual Relevance: The degree to which a stimulus aligns with the system’s current internal state and prior experiences. Highly relevant stimuli receive more attention.

**Neural Noise**: Neural Noise: Random fluctuations in neuronal activity. While seemingly detrimental, neural noise can be a signal for attention, highlighting areas of the system where the model is most uncertain and therefore needs adjustment.

**Elaboration & Examples:**

The free energy principle suggests that systems don’t passively receive information; they actively shape their perception. Consider a visual scene: a robot (or a human) doesn't register *every* detail. Instead, it detects a bright flash—a high prediction error—and directs its attention to that location. This action reduces the “surprise” associated with the unexpected event, contributing to a more stable and accurate internal model.

Bayesian inference plays a crucial role. The system’s prior beliefs about the environment influence the weighting applied to new sensory data.  If the system already expects to see a particular object in a given context, it will assign less weight to evidence confirming that expectation, while assigning greater weight to evidence that contradicts it.

Neural noise, often dismissed as random static, can be a critical component of the attention process. The system is most likely to attend to areas where the predicted and actual sensory input diverge significantly.  This highlights areas where the internal model is most uncertain and requires refinement.

**Mnemonics:**

*   **FEP (Free Energy Principle):** "Find Easy Paths" –  The system seeks the easiest, most predictable path to minimize surprise.
*   **Bayesian Inference:** "Believe and Verify" – Use Bayesian methods to assess the evidence and update your beliefs.