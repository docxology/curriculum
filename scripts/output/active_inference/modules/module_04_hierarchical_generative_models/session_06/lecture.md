# Hierarchical Generative Models

## Learning Objectives

- Understand hierarchical prediction

---

## Introduction to Recurrent Predictive Models

Welcome back to Hierarchical Generative Models. In our previous sessions, we’ve explored foundational concepts within predictive processing – the idea that the brain, and potentially other complex systems, operates by constantly predicting its sensory input and adjusting its internal models based on discrepancies, or prediction errors. We established the core framework: a hierarchical system where lower levels predict the activity of higher levels, and these predictions are refined through error signals. Today, we delve into a crucial component of this framework: recurrent predictive models, specifically focusing on models incorporating recurrent connections. These connections represent a significant enhancement to the basic hierarchical architecture, allowing for the modeling of temporal dependencies – essentially, the ability to ‘remember’ past states when making predictions. Think of it like trying to anticipate the next word in a sentence; you don’t just consider the preceding word, but the entire context of the conversation.

---

## Main Topic 1: Recurrent Connections – The Memory Element

The core of a recurrent predictive model lies in its recurrent connections. A **recurrent connection**: is a connection that feeds the output of a unit back into itself or another unit within the same network. This feedback loop allows information to persist within the system, creating a form of “memory.” Imagine a simple weather model. A basic predictive model might predict temperature based solely on current conditions. However, a recurrent model would also consider the temperature from the previous day, the previous week, and so on. This historical context drastically improves the accuracy of the prediction.  Consider a financial model; a purely static model would ignore past market performance, whereas a recurrent model incorporates time series data to anticipate future trends. The strength of these connections – the magnitude of the weights – determines how much influence the past has on the present prediction. Varying these weights effectively allows us to tune the model's ‘memory’. Furthermore, recurrent connections provide a mechanism for capturing temporal dependencies – patterns that change over time.

---

## Main Topic 2: Prediction Error & Precision Weighting

The process of generating predictions in a recurrent predictive model doesn’t simply involve calculating the difference between a predicted value and an observed value. Instead, we focus on **prediction error**:  the difference between a model’s prediction and the actual observed signal. However, not all prediction errors are created equal. A recurrent model incorporates **precision weighting**: a mechanism that assigns different weights to different prediction errors.  This is based on the principle that the brain doesn’t treat all sensory input equally. For instance, if a model predicts a slight drop in temperature but the actual temperature remains the same, the error signal will be significantly lower than if the temperature increased dramatically.  This differential weighting reflects the idea that the brain assigns more importance to information that it believes is most relevant to its goals.  Specifically, prediction errors are weighted inversely proportional to their magnitude; larger errors result in smaller weights, and vice versa.  This weighting is crucial for efficient learning and adaptation within the hierarchical system.  For example, a minor misprediction of a stock price change would have less impact than a major one – reflecting our tendency to learn from significant deviations.

---

## Main Topic 3: Hierarchical Prediction with Recurrence

Let’s illustrate this with an example: a model predicting human movement. The lowest level might predict the instantaneous position of individual muscles. The next level predicts the position of limbs based on these muscle predictions. The highest level might then predict the overall movement – such as walking or running – based on the limb predictions. Crucially, the limb predictions themselves would be recurrent. They would consider the previous limb positions, creating a temporal chain of predictions. This feedback loop is vital for generating smooth, coordinated movements. Consider a robotic arm learning to reach for a target. Initially, the arm might jerk around erratically. However, through iterative prediction and error correction – driven by the recurrent connections – the arm will learn to move smoothly and accurately.  The model doesn't simply react to immediate sensory input; it actively constructs a temporal representation of the task, allowing for anticipatory movements.

---

## Main Topic 4: Mathematical Formulation – The Recurrent Predictive Equation

The fundamental equation governing this process can be represented as follows:

`x_t = f(x_{t-1}, y_{t-1}, θ)`

Where:

*   `x_t` is the predicted value at time *t*.
*   `y_t` is the actual observed value at time *t*.
*   `θ` represents the model parameters (including the weights of the recurrent connections).

This equation highlights the key elements: the current prediction (`x_t`) is a function of the previous prediction (`x_{t-1}`), the actual observed value (`y_t`), and the model's parameters. The recurrent connection ensures that the previous prediction is a significant input to the current prediction, effectively incorporating temporal information.

---

## Main Topic 5: Scaling Predictive Processing – Linking to Higher Levels

The concept of “scaling” in predictive processing refers to the ability of lower-level predictions to influence higher-level predictions.  Recurrent connections are a vital component of this scaling process.  Without the ability to ‘remember’ previous states, the system would be unable to effectively scale its predictions. Consider a visual system.  The lower levels of the system are responsible for detecting edges and shapes. These basic features are then combined by higher-level areas to recognize objects – such as faces or animals.  Recurrent connections allow the lower-level areas to continuously refine their representations based on past experience, ensuring that the system’s representations are appropriately scaled to the task at hand.  For instance, the system learns to differentiate between a blurry image of a dog and a clear image of a dog, because the recurrent connections allow it to build a robust representation of a dog, even in challenging conditions.

---

## Main Topic 6: Examples & Applications

Let’s consider some concrete examples.  In speech recognition, recurrent neural networks (RNNs) – a specific type of recurrent model – are used to process sequential audio data, accounting for the temporal context of speech sounds. Similarly, in natural language processing, recurrent models are used to generate text, predicting the next word in a sentence based on the preceding words. In neuroscience, research suggests that recurrent connections in the brain play a crucial role in motor control, allowing for the smooth and coordinated execution of movements.  Furthermore, economic models incorporating recurrent connections can better capture the dynamics of financial markets, where past performance significantly influences future trends.

---

## Summary & Key Takeaways

Today’s session focused on recurrent predictive models and their critical role within hierarchical generative systems. We established that **recurrent connections** provide the ability to ‘remember’ past states, allowing models to capture temporal dependencies and account for past experience. We introduced the concept of **precision weighting**, a mechanism for differentially weighting prediction errors based on their magnitude. The fundamental equation `x_t = f(x_{t-1}, y_{t-1}, θ)` illustrates the iterative process of prediction and error correction. Finally, we explored various applications, from motor control to financial modeling. The ability to incorporate temporal information is a hallmark of sophisticated predictive systems, and recurrent models represent a powerful tool for understanding and modeling these systems.  The key takeaway is that hierarchical generative models, particularly those employing recurrent connections, offer a compelling framework for explaining complex, dynamic phenomena across a wide range of disciplines.