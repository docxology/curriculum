# Foundations of Active Inference - Laboratory Exercise 1

## Lab Focus: Free Energy Minimization

---

**Module: Foundations of Active Inference – Lab 1: Free Energy Minimization**

**Lab Number:** 1
**Lab Focus:** Free Energy Minimization

**1. Brief Background (87 words)**

Following the lecture’s introduction to Active Inference, this lab explores the core mechanism driving adaptive behavior: minimizing surprise. We’ll investigate how the brain constructs predictive models and actively shapes experience. The concept of Variational Free Energy (VFE) is central. VFE represents the difference between a predicted model and actual sensory input – a mismatch we actively reduce through action. This lab will utilize a simple visual stimulus to illustrate this principle, mimicking the cup-reaching example discussed in the lecture.

**2. Lab Objectives:**

*   Manipulate a visual stimulus to systematically increase or decrease the perceived “surprise” related to its location.
*   Record changes in participant’s reported perception of the stimulus location.
*   Quantify the relationship between perceived surprise and corresponding perceptual adjustments.
*   Develop an intuitive understanding of how action can reduce VFE.
*   Document observations to illustrate the predictive coding loop.

**3. Materials and Equipment:**

*   **Stimulus Device:** Laptop with screen and software (e.g., MATLAB with Psychtoolbox, Python with PsychoPy) – configured to display a moving dot.
    *   Dot Size: 10 pixels diameter
    *   Dot Color: White (#FFFFFF)
    *   Dot Velocity: 0.5 degrees/second (adjustable)
    *   Background Color: Black (#000000)
*   **Participant Interface:**
    *   Comfortable chair
    *   Headset with microphone (for feedback collection)
    *   Tablet or smartphone (for response recording – optional)
*   **Data Collection Hardware:**
    *   Stopwatch (accurate to 0.1 second)
*   **Data Recording Software:**  [INSTRUCTOR TO SPECIFY SOFTWARE] – capable of recording participant responses and stimulus parameters.
*   **Calibration Tools:** Ruler, Whiteboard.

**4. Safety Considerations (⚠️)**

*   **Eye Strain:**  Participants should take regular breaks (every 20 minutes) to reduce eye strain.  The screen brightness should be adjusted to a comfortable level. [INSTRUCTOR: Monitor participant comfort levels].
*   **Electrical Safety:** Ensure the laptop and any connected peripherals are functioning correctly to avoid electrical hazards. [INSTRUCTOR: Check equipment functionality before each session.]
*   **Ergonomics:**  Participants should maintain a comfortable posture to avoid musculoskeletal discomfort. [INSTRUCTOR: Observe participant posture and provide adjustments if needed].
*   **Software Bugs:** The software may contain bugs. Report any unexpected behavior to [INSTRUCTOR] immediately.

**5. Procedure:**

1.  **Setup (2 minutes):**  Participants are seated comfortably in front of the computer screen. The software is launched, and the dot stimulus is displayed. Ensure the participant can clearly see the dot.
2.  **Baseline Measurement (3 minutes):**  Without any intervention, participants are asked to report, via the microphone, their subjective perception of the dot's horizontal position (left/right) on a scale of -3 to +3 (where -3 is far left, +3 is far right, 0 is centered). Record the average response every 30 seconds.
3.  **Manipulation – Shift (5 minutes):** The software is instructed to move the dot horizontally by +1 degree/second.  Participants continue to report their subjective perception of the dot’s horizontal position at 30-second intervals.
4.  **Manipulation – Return (5 minutes):** The software is instructed to return the dot to its original position. Participants continue to report their subjective perception of the dot’s horizontal position at 30-second intervals.
5.  **Debriefing (1 minute):** [INSTRUCTOR: Conduct a brief debriefing session to clarify any questions and discuss the experiment’s objectives.]

**6. Data Collection:**

| Time (seconds) | Participant | Dot Position (Reported) | Dot Position (Actual) |
|---|---|---|---|
| 0 |  |  |  |
| 30 |  |  |  |
| 60 |  |  |  |
| 90 |  |  |  |
| 120 |  |  |  |
| 150 |  |  |  |
| 180 |  |  |  |

**7. Analysis Questions:**

1.  How did the participant’s reported perception of the dot’s position change when the dot was moving to the right? What does this suggest about their predictive model?
2.  How did the participant’s reported perception of the dot’s position change when the dot was returning to its original position?  What does this illustrate about the brain’s tendency to reduce surprise?
3.  Connect the observed changes in perception to the concept of Variational Free Energy.  How might the brain be minimizing VFE in this scenario?
4.  How might this lab activity relate to the idea of perception-action loops described in the lecture?

**8. Expected Results:**

Participants will likely report a shift in their perceived dot position when the dot moves to the right.  As the dot moves, the participant will likely increase their reported perception of its position to match the moving dot.  When the dot returns to its original position, the participant’s reported perception should shift back to the center. This demonstrates that the participant is actively adjusting their perceptual state to reduce the perceived discrepancy (surprise) between the predicted and actual location of the dot, thereby minimizing VFE.  This directly supports the core tenets of Active Inference.