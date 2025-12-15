# Applications: AI & Robotics

## Learning Objectives

- Apply AI concepts

---

## Introduction

Welcome back to the Applications of AI & Robotics module. Last week, we explored reinforcement learning and its application in robotic navigation. This session delves into a fascinating intersection of AI and robotics – deep learning combined with the framework of *Active Inference*. Until now, much of our discussion has focused on passively observing and reacting to stimuli. Active Inference proposes a fundamentally different approach: an agent actively seeks to *understand* its environment and predict its future, driving its actions accordingly. This isn’t simply about learning a policy; it’s about building an internal model of the world and using it to anticipate and shape events. Consider a human reaching for a cup of coffee. We don’t just react to the visual stimulus of the cup; we *predict* the cup will be where we expect it to be, and our action is driven by that prediction. Active Inference attempts to replicate this embodied understanding in artificial systems. The core idea is that an agent’s perception isn't a raw, unfiltered view of the world, but rather an inference – a probabilistic calculation – based on its prior beliefs and the sensory data it receives. For instance, a robot’s vision system doesn’t just detect ‘red’; it infers ‘apple’ based on a learned model of what an apple looks like.

---

## Main Topic 1: Representation Learning and Predictive Coding

At the heart of Active Inference lies *representation learning*. Traditionally, in machine learning, features are hand-engineered – we tell the algorithm exactly what to look for. However, Active Inference suggests that intelligent agents learn representations in a fundamentally different way. They build internal models of the world, and these models are constantly being refined through a process of *predictive coding*. This process fundamentally states that the brain (and by extension, intelligent systems) doesn’t simply respond to sensory input, it *predicts* what that input *should* be, and then compares this prediction to the actual input. The difference between the prediction and the actual input – the *prediction error* – drives learning and action. For example, consider a visual scene. The system predicts what it *should* see (e.g., a wall), and when the actual image deviates from this prediction, a prediction error signal is generated. This error signal then triggers an action – moving the head to gain a better view and reduce the error. Consider a baby learning about a ball. Initially, the baby’s model will be inaccurate, leading to large prediction errors.  As the baby interacts with the ball, the model is refined, reducing the prediction error and leading to more accurate perception and motor control.

### 1.1 Bayesian Inference

This predictive coding framework is underpinned by Bayesian inference. Bayesian inference allows us to update our beliefs in light of new evidence. In the context of Active Inference, the prior belief represents the agent's initial assumptions about the world, while the sensory data acts as evidence. The agent then uses Bayes’ theorem to calculate the posterior probability – the updated belief – which guides subsequent predictions and actions. This is analogous to how we update our beliefs based on new evidence in our daily lives – consider a situation where you initially assume it will rain, but the sky remains clear.

---

## Main Topic 2: Generative Adversarial Networks (GANs) & Active Inference

GANs, particularly, have become increasingly intertwined with Active Inference. GANs consist of two neural networks: a *generator* and a *discriminator*. The generator attempts to create realistic data (e.g., images), while the discriminator tries to distinguish between real and generated data. Active Inference proposes that the generator can be viewed as the agent's *motor system* actively shaping its sensory environment to reduce prediction error.  For instance, imagine a robot trying to learn about a new object. The discriminator can be seen as representing the sensory evidence, and the generator, through motor actions, attempts to create sensory data that aligns with its internal model – reducing the prediction error. Consider a robot learning to grasp an object. Initially, its attempts will be clumsy, generating high prediction errors (e.g., dropping the object).  Through repeated attempts, the generator learns to adjust its motor commands, producing sensory data that matches its internal model – a hand grasping the object successfully.  This process mimics the active exploration of a visual scene combined with the goal of minimizing prediction error.

### 2.1 Active Inference and Motor Control

Specifically, motor commands aren’t just outputs of a learned policy.  Within Active Inference, motor commands are *predictions* about the sensory consequences of those actions. The system actively generates motor commands to minimize these prediction errors, rather than passively reacting to a reward signal. This contrasts sharply with traditional reinforcement learning where the agent is often told *what* to do, whereas Active Inference empowers the agent to *discover* the optimal actions through active exploration.

---

## Main Topic 3:  The Role of Priors

Crucially, the internal model isn't built from scratch. It's initialized with *priors* – prior beliefs about the world. These priors can be based on prior experience, learned knowledge, or even just basic assumptions about the physical world (e.g., "objects tend to move”).  For example, a robot exploring a new room will initially assume that objects are solid and that it can move freely through the space.  These priors influence the agent's initial predictions and guide its exploration. Consider a robot learning about gravity. Initially, the robot might assume that objects will float upwards, leading to erratic behavior.  As the robot experiences gravity, the prior belief is updated, leading to more accurate motor control.

---

## Main Topic 4:  Applications - Robotics and Beyond

The implications of Active Inference extend far beyond robotics. It provides a framework for understanding a wide range of cognitive phenomena, including perception, motor control, and even decision-making.  For instance, consider human navigation.  We don’t consciously plan every step; we rely on an internal model of the world, constantly predicting and correcting our movements. This aligns perfectly with the Active Inference framework.  Imagine a person walking down a street. The system is constantly predicting where the sidewalk, obstacles, and other people will be, adjusting its trajectory to avoid collisions and maintain a comfortable path. Consider a study where participants were asked to follow a moving dot. The results showed that participants consistently steered their gaze towards the expected location of the dot, even when the dot moved in a way that contradicted their initial predictions – a clear demonstration of Active Inference in action.

---

## Summary

This session has explored the core principles of Active Inference and its connection to deep learning, particularly through the lens of GANs and representation learning.  Key takeaways include:  representation learning is driven by predictive coding and minimizing prediction error, internal models are initialized with prior beliefs, and motor commands are active predictions about sensory consequences. Active Inference provides a powerful framework for understanding intelligent behavior – not just in robots, but also in humans and other animals. The framework's emphasis on active exploration and causal inference represents a significant shift from traditional, passive approaches to AI. By understanding and applying these concepts, we can begin to design and build intelligent systems that are truly capable of understanding and interacting with the world around them. Further exploration should focus on specific implementations and experimental validation of Active Inference models.