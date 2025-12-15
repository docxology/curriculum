# Variational Inference

## Learning Objectives

- Minimize ELF

---

## Introduction to Variational Free Energy

Welcome back to Variational Inference. In our previous sessions, we’ve established the fundamental problem we’re tackling: approximating Bayesian inference when exact inference is intractable. We’ve introduced the concepts of probability distributions, prior distributions, and likelihood functions. Recall that Bayesian inference relies on combining these components to derive our posterior distribution – a crucial representation of our belief about a system’s state given observed data. However, calculating the posterior analytically is often impossible, especially when dealing with complex models and high-dimensional data. This is where variational inference steps in. We’ve seen that we can approximate the true posterior with a simpler, tractable distribution – a *variational distribution*. Today, we delve into a central component of this process: the *variational free energy* (VFE), and how we use it to minimize the distance between this approximation and the true posterior.

---

## Main Topic 1: The ELF Formulation – A Starting Point

The foundation for approximating the posterior using variational inference lies in the *ELF formulation*, or *Evidence Lower Bound formulation*. The ELF essentially provides a lower bound on the marginal likelihood – the probability of observing the data given a particular model and parameter values.  Mathematically, the marginal likelihood is represented as:

L(θ|x) = ∫ p(x|θ) p(θ) dx

where:
*  L(θ|x) is the marginal likelihood.
*  θ represents the model parameters.
*  x represents the observed data.
*  p(x|θ) is the likelihood function.
*  p(θ) is the prior distribution.

Because directly calculating this integral is often impossible, we aim to find a distribution q(θ) such that  log q(θ) gives an *evidence lower bound* on log L(θ|x).  This lower bound provides a tractable alternative. We'll be focusing on minimizing this lower bound.

---

## Main Topic 2: Defining and Minimizing the Variational Free Energy

The *Variational Free Energy*, often denoted as F<sub>q</sub>(θ), is precisely that lower bound.  It’s a scalar value that quantifies the difference between our chosen variational distribution q(θ) and the true posterior distribution p(θ|x).  Mathematically:

F<sub>q</sub>(θ) = -log q(θ)

The variational free energy is an *energy function*, analogous to the energy functions used in physics, where minimizing the energy function corresponds to finding the state of minimum energy. In this case, minimizing F<sub>q</sub>(θ) seeks to find the variational distribution q(θ) that is closest to the true posterior, as measured by the evidence lower bound.  Consider this: if we were to represent the true posterior as a landscape, minimizing F<sub>q</sub>(θ) is akin to finding the lowest point on that landscape, guaranteeing a tight bound on the evidence.

For example, if we’re modeling the position of a robot using a Gaussian distribution, and our variational distribution also uses a Gaussian, minimizing the VFE will result in parameters (mean and variance) of the Gaussian approximation that are as close as possible to the true parameters defining the posterior. This is a crucial step as it allows us to efficiently approximate the intractable posterior.

---

## Main Topic 3: Optimization – Gradient Descent

The process of minimizing the variational free energy involves optimization. We employ techniques like *gradient descent* to iteratively adjust the parameters of our variational distribution until we reach a minimum. Gradient descent operates on the gradient of the VFE with respect to the parameters of the variational distribution.  The gradient, denoted as ∇<sub>θ</sub>F<sub>q</sub>(θ), points in the direction of the steepest increase of the VFE. Therefore, moving in the *opposite* direction of the gradient will decrease the VFE.

Mathematically, the update rule for gradient descent is:

θ<sub>t+1</sub> = θ<sub>t</sub> - η ∇<sub>θ</sub>F<sub>q</sub>(θ<sub>t</sub>)

where:
* θ<sub>t+1</sub> is the parameter value at the next iteration.
* θ<sub>t</sub> is the parameter value at the current iteration.
* η (eta) is the learning rate – a hyperparameter that controls the step size.
* ∇<sub>θ</sub>F<sub>q</sub>(θ<sub>t</sub>) is the gradient of the VFE evaluated at the current parameter values.

Consider a simple example: let’s say we’re modeling the height of individuals in a population with a Gaussian distribution. The gradient descent algorithm would iteratively adjust the mean and variance of the Gaussian distribution to minimize the VFE, bringing the distribution closer to the true posterior distribution.

---

## Main Topic 4: The Role of the Learning Rate (η)

The learning rate, η, is a critical hyperparameter in gradient descent. A too-large learning rate can lead to instability and the algorithm bouncing around the minimum, while a too-small learning rate can result in slow convergence.  Choosing an appropriate learning rate is crucial for efficient optimization. Adaptive learning rate methods, such as Adam or RMSprop, automatically adjust the learning rate for each parameter, often leading to faster and more stable convergence than standard gradient descent.  For instance, imagine trying to navigate a very hilly landscape – a small step size will ensure you don’t overshoot the valley, but a large step size may cause you to jump over it entirely.

---

## Main Topic 5: Practical Considerations & Examples

Let's consider a more concrete example:  We want to model the firing rate of a neuron.  We assume the neuron’s firing rate follows an exponential distribution.  Our variational distribution will also be a distribution over the exponential parameters (rate and offset).  The VFE is then minimized to find the best parameters for this approximation.

Another example: Suppose we are trying to learn the parameters of a Markov chain. The VFE is minimized using gradient descent to estimate the transition probabilities and state probabilities, giving us a tractable representation of the underlying dynamical system. The success of the approximation depends heavily on the choice of the variational distribution q(θ).

---

## Summary and Key Takeaways

Today's session focused on the variational free energy and its role in approximating Bayesian inference. We've established that the VFE provides a lower bound on the marginal likelihood, representing a measure of how well our variational distribution q(θ) approximates the true posterior distribution p(θ|x).  We've learned that the VFE is minimized using optimization techniques, most notably gradient descent.  The learning rate (η) is a crucial hyperparameter that controls the step size during optimization.  Finally, we saw how this process allows us to approximate the intractable posterior, enabling us to make predictions and inferences even when exact inference is impossible. The success of this method hinges on careful selection of the variational distribution and the appropriate tuning of hyperparameters like the learning rate. The variational free energy is a cornerstone of variational inference, providing a powerful tool for approximating complex Bayesian models.