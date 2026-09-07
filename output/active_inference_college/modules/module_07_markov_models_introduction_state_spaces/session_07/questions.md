# Markov Models – Introduction & State Spaces - Comprehension Questions

**Total Questions**: 10  
**Multiple Choice**: 5 | **Short Answer**: 3 | **Essay**: 2

---

**Question 1:** Which of the following best describes the core principle of the Markov Property?
A) The future state depends on the entire history of the system.
B) The system’s behavior is entirely predictable regardless of past events.
C) The future state depends only on the present state.
D) The system requires constant external input to maintain its current state.
**Answer:** C
**Explanation:** The Markov Property dictates that the system’s future state is solely determined by its current state, disregarding any prior history or influences. This "memorylessness" is fundamental to the model's structure.

**Question 2:** A website is tracking user behavior. Which of the following would *not* be a suitable state for a Markov model to analyze?
A) User’s current page type (product, category, homepage)
B) The user’s browsing history for the past week.
C) The time of day the user is accessing the website.
D) The current page the user is viewing.
**Answer:** B
**Explanation:** The Markov Property focuses on the *present* state; tracking extensive past history is unnecessary and computationally expensive. The model only needs the current page type to predict the next transition.

**Question 3:** In the context of Markov models, what does “transition probability” represent?
A) The likelihood of the system remaining in its current state.
B) The probability of moving from one state to another.
C) The total number of possible states in the system.
D) The average time spent in a particular state.
**Answer:** B
**Explanation:** Transition probabilities quantify the likelihood of moving from one state to another, representing the core mechanism of the Markov model’s predictive capabilities. These probabilities are derived from observed state transitions.

**Question 4:**  The wooden gear set lab exercise is designed to demonstrate which key concept of Markov Models?
A) Calculating complex differential equations.
B) Understanding the influence of friction on system behavior.
C) Observing and analyzing state transitions in a simulated system.
D)  Optimizing gear ratios for maximum mechanical efficiency.
**Answer:** C
**Explanation:** The lab focuses on directly observing how the gears change states (rotation directions) based on their current positions, illustrating the fundamental Markovian principle of state transitions.

**Question 5:**  Why is the “memorylessness” characteristic of Markov Models a significant simplification?
A) It allows for extremely complex and detailed simulations.
B) It reduces the computational burden and model complexity.
C) It guarantees perfect prediction accuracy in all circumstances.
D) It eliminates the need for any initial data input.
**Answer:** B
**Explanation:** By discarding past history, Markov Models create significantly simpler and more manageable models, facilitating analysis and prediction without being burdened by a vast amount of historical information.

**Question 6:**  Describe the relationship between the current state and future state within a Markov model?
**Answer:** The current state dictates the future state within a Markov model. The model assumes that the future state is determined solely by the system’s present condition, ignoring any influence from prior states or events. This focuses on immediate, present conditions for predicting subsequent states.

**Question 7:**  Explain how the wooden gear set can be used to practically demonstrate state transitions in a Markov Model?
**Answer:**  By observing the rotation direction of each gear, we can identify distinct states. Transitions occur when gears rotate, changing from one state to another. The frequency of these transitions, guided by the current gear configurations, illustrates how transition probabilities govern the system's behavior within a Markov model.

**Question 8:**  Considering a website traffic model, what information *would* need to be considered beyond just the current page type to build a more comprehensive Markov model?
**Answer:**  To build a truly comprehensive model, factors such as time of day, user session duration, and referring website would need to be incorporateD) These additional data points would provide a more accurate representation of the system's dynamics and allow for a richer set of predictive insights.

**Question 9:**  Describe a real-world application where the principles of Markov Models could be applied to predict future outcomes.?
**Answer:**  Stock market analysis can utilize Markov models. The current stock price, trading volume, and market indicators (like interest rates) could be considered the “state.” Transitions represent changes in stock prices, allowing the model to predict future price movements based on current market conditions, similar to how a website traffic model predicts user behavior.

**Question 10:**  Discuss how the concept of "state transitions" relates to both the wooden gear set experiment and predicting website user behavior.?
**Answer:** In both scenarios, "state transitions" represent changes in condition - the gear’s rotation direction or a user’s page visit.  Understanding these transitions, tracked through observation and data collection, allows us to build a predictive model. Whether analyzing gears or website user behaviour, the key is recognizing and modelling the shift between specific states.