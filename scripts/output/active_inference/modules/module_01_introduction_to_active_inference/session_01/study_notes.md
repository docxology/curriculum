# Introduction to Active Inference - Study Notes

## Key Concepts

**Introduction to Active Inference: Study Notes**

## Expanding on Key Concepts

**Generative Model**:  These models are often hierarchical, meaning they consist of multiple levels of abstraction. For example, a model of a 'cat' might include features like 'fur', 'whiskers', ‘four legs’ and ‘meows’. The brain continually refines these models based on experiences.  *Memory Aid:* “Gen” – Generate, the foundation of the model.

**Free Energy**: This concept is central to Active Inference.  It’s formally defined as the sum of a variational lower bound on the marginal likelihood of the data, given the model and the action.  Don’t worry about the exact mathematical formulation for now – the core idea is a drive to *reduce* this quantity. *Memory Aid:* “Free Energy = Fear + Energy” – representing the discomfort of uncertainty (fear) and the energy required for action.

**Perception**:  Consider a visual scene. Your brain doesn’t simply “see” a red apple. Instead, it integrates incoming visual data with its prior beliefs about color, shape, and texture, ultimately generating a *perception* of a red apple. This highlights how perception is always influenced by the generative model. *Example:* Initially, the model might predict a green apple due to the lighting conditions; perception corrects this by highlighting the red hues.

**Action**: Actions aren't just random movements. They're carefully designed to minimize free energy. If your model predicts a warm room and you’re cold, you take an action (e.g., put on a sweater) to reduce the discrepancy between your predicted and actual temperature. *Mnemonics:* “Act” – Action, targeted towards reducing uncertainty.

**Sensory Input**:  Always interpreted, never simply received. The brain automatically filters and interprets incoming sensory information, using the generative model to make sense of it. It’s crucial to understand that sensory data is always relative to the model. *Example:* The same sound might be perceived as a bird chirp by one person and a car horn by another, depending on their prior expectations and model of the environment.

## Additional Points

*   **Bayesian Inference**: Active Inference relies heavily on Bayesian statistical methods to update the generative model based on new evidence.
*   **Prediction Error**:  The difference between the predicted sensory input and the actual sensory input.  Minimizing prediction error is the core driving force of active inference.
*   **Self-Modeling**: The brain creates a model of itself, which plays a key role in coordinating actions and predicting sensory consequences.
*   **Hierarchical Models**: Active Inference often employs hierarchical models with multiple levels of abstraction, allowing for efficient representation of complex environments.