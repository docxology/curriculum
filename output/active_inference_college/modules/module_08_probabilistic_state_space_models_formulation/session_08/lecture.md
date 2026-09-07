# Probabilistic State-Space Models – Formulation

## Learning Objectives

- Understand model equations

---

## Introduction

Welcome back to Probabilistic State-Space Models. In the preceding sessions, we’ve explored the fundamental building blocks: stochastic processes, probability distributions, and the concept of perception-action loops. We’ve established that these loops, common across biological systems and artificial intelligence, often involve an agent interacting with an environment, receiving sensory input, and taking actions that modify the environment, and consequently, the agent’s internal state. Today, we delve into the heart of state-space modeling – formalizing these loops through a set of mathematical equations. These equations allow us to precisely describe how the agent’s state evolves over time, how it is influenced by sensory input, and how actions affect that evolution. We’ll be focusing on the core equations of state-space models, understanding their components, and appreciating their significance. Consider a simple example: a robot navigating a room. Its state might be its position and orientation; the sensory input would be data from its cameras and sensors; and its actions would be movements – turning left, turning right, moving forward.

---

## Main Topic 1: State Equations

The first set of equations we’ll examine are the **state equations**. These equations define how the agent's internal state *x<sub>t</sub>* evolves from one time step *t* to the next. They represent the underlying dynamics of the system. Generally, the state equation takes the form:

*x<sub>t+1</sub> = f(x<sub>t</sub>, u<sub>t</sub>, w<sub>t</sub>)*

Let’s break down this equation. *x<sub>t</sub>* represents the state at time *t*. *u<sub>t</sub>* represents the control input or action taken at time *t*. *w<sub>t</sub>* represents an unobserved process noise term, accounting for inherent uncertainties in the system. The function *f* encapsulates the dynamics of the system – how the state changes based on the current state, the action, and the noise.

**Example 1:** A simple model of a pendulum. The state could be the angle θ and the angular velocity ω. The state equation might be:

*ω<sub>t+1</sub> = θ<sub>t</sub>  (This is a simplified model; a more complex one would include damping terms.)*

Here, the angular velocity *ω<sub>t</sub>* at time *t* is directly determined by the angle *θ<sub>t</sub>* at time *t*.

**Example 2:** In a population model, the state *x<sub>t</sub>* could represent the population size at time *t*. The state equation might be:

*x<sub>t+1</sub> = r * x<sub>t</sub> (1 - x<sub>t</sub>)*

Where *r* is the growth rate. This simple equation reflects the logistic growth model, where the population size increases proportionally to the current population size, but is limited by a carrying capacity.

---

## Main Topic 2: Measurement Equations

The second set of equations are the **measurement equations**. These equations describe how the agent’s state is observed through its sensors. They relate the state *x<sub>t</sub>* to the observed data *y<sub>t</sub>*.  The general form is:

*y<sub>t</sub> = h(x<sub>t</sub>, v<sub>t</sub>)*

*y<sub>t</sub>* is the observed data at time *t*. *h* is a function that maps the state to the observed data. *v<sub>t</sub>* represents another unobserved process noise term, accounting for noise in the measurement process.

**Example 3:**  Consider a robot equipped with a laser rangefinder. The state is the robot’s position (x, y). The observed data is the distance *y<sub>t</sub>* to a particular point. The measurement equation could be:

*y<sub>t</sub> = sqrt((x<sub>t</sub> - x<sub>t+1</sub>)<sup>2</sup> + (y<sub>t</sub> - y<sub>t+1</sub>)<sup>2</sup>)*

This equation calculates the distance between the robot’s current and next positions, representing the laser reading.

**Example 4:**  Imagine monitoring a chemical reaction. The state *x<sub>t</sub>* could be the concentration of reactant A at time *t*.  The observed data *y<sub>t</sub>* could be the measured concentration of the same reactant. The measurement equation might be:

*y<sub>t</sub> = x<sub>t</sub> + v<sub>t</sub>*

where *v<sub>t</sub>* represents measurement error.

---

## Main Topic 3: Process and Measurement Noise

The terms *w<sub>t</sub>* and *v<sub>t</sub>* are crucial for realistic modeling. They represent noise – inherent uncertainty – in both the state evolution (process noise) and the measurements.

**Process Noise (w<sub>t</sub>):** This represents uncertainties in the dynamics of the system.  It’s often assumed to be Gaussian, with a mean of zero and a covariance matrix *Q*. This indicates that we don’t know exactly how the system will evolve; there’s some randomness involved.

**Measurement Noise (v<sub>t</sub>):** This represents the inaccuracy of our sensors. It’s also typically assumed to be Gaussian with a mean of zero and a covariance matrix *R*.

**Example 5:**  Let’s return to the pendulum.  The process noise *w<sub>t</sub>* could represent variations in friction or air resistance.  The measurement noise *v<sub>t</sub>* would represent the limitations of the angle sensor – it might not perfectly measure the true angle due to sensor inaccuracies.

---

## Main Topic 4: Model Parameter Estimation

The equations we’ve discussed are the *model* equations.  However, in reality, we rarely know the exact values of *f*, *h*, *Q*, and *R*. We must estimate these parameters from observed data. This is typically done using Bayesian inference, where we calculate the posterior distribution of the parameters given the data.

**Example 6:** Suppose we are building a model of a stock price.  We can estimate the parameters of the state equation (e.g., the growth rate *r*) and the measurement equation (e.g., the covariance of the measurement noise *R*) by comparing the model’s predictions to the actual stock prices over time.

---

## Main Topic 5: Kalman Filter – A Brief Overview

The Kalman filter is an algorithm that efficiently computes the optimal estimate of the state and the associated uncertainties given a sequence of noisy measurements. It iteratively applies the state equations and measurement equations, along with the Kalman gain, to update the state estimate and covariance matrix.  A full treatment of the Kalman filter is beyond the scope of this lecture, but it’s essential to understand its role as the computational engine behind state-space models.

---

## Summary

Today’s session has covered the fundamental mathematical equations of state-space models: state equations, measurement equations, process noise, and measurement noise. We've explored how these equations represent the dynamics of a system, how it’s observed, and how noise affects our understanding of the system. We’ve also introduced the concept of model parameter estimation and briefly touched upon the Kalman filter – the algorithm that makes these models practically useful. The ability to formally represent perception-action loops through state-space models provides a powerful framework for analyzing and controlling complex systems, ranging from robotics and control to biology and finance.  Further sessions will delve deeper into specific Kalman filter implementations and explore advanced applications.