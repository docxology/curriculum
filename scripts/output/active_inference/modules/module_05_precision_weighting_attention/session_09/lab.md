# Precision Weighting & Attention - Laboratory Exercise 9

## Lab Focus: Selective Perception

---

**Module: Precision Weighting & Attention**
**Lab Number: 9**
**Lab Focus: Selective Perception**

**1. Brief Background (90 words)**

This laboratory exercise builds upon the concepts introduced in the Precision Weighting & Attention lecture, specifically the Free Energy Principle and its role in shaping our perceptual processes. We will investigate how systems, like a simulated robot, dynamically adjust their focus to minimize 'surprise' – a core tenet of the FEP. Students will manipulate sensory input, mimicking the selective attention observed in biological systems, to directly experience the impact of weighted perception on information processing. This activity will provide a tangible demonstration of how internal models are constructed and refined to achieve efficient sensory integration.

**2. Lab Objectives (4 bullets)**

*   Construct a simulated robotic system with adjustable attention weights.
*   Manipulate a stimulus (visual pattern) to observe its impact on system ‘surprise’.
*   Record data on system response (e.g., activation level) as a function of stimulus characteristics.
*   Analyze the relationship between stimulus weight and system output.
*   Develop an understanding of how attention mechanisms contribute to optimal inference.

**3. Materials and Equipment**

*   **Computer 1 (Instructor Use):**
    *   Laptop with MATLAB (R2023a or later) installed.
    *   MATLAB Code: ‘Robot_Attention_Simulation.m’ (provided)
*   **Computer 2 (Student Use):** Laptop with MATLAB installed.
*   **Visual Stimulus Display:** LCD Monitor (minimum 19" - 1024 x 768 resolution)
*   **Calibration Target:** Printed square target (20mm x 20mm) with a 10mm x 10mm cross at the center.
*   **USB Mouse:** For controlling the robot's attention mechanism.
*   **Calibration Ruler:** For verifying stimulus size.
*   **Notebook and Pen:** For recording observations.

**4. Safety Considerations (⚠️)**

*   **Eye Strain:** Take frequent breaks (every 20 minutes) to minimize eye strain from prolonged screen viewing.
*   **Electrical Safety:** Ensure all cables are properly connected and avoid spilling liquids on electrical equipment. [INSTRUCTOR] – Monitor students' posture to prevent strain.
*   **Equipment Damage:** Handle equipment with care to avoid damage. Do not attempt to disassemble or modify any equipment.
*   **Potential for Discomfort:** If any student experiences discomfort (e.g., headache, dizziness), immediately discontinue the experiment and inform the [INSTRUCTOR].

**5. Procedure (7 steps)**

1.  **Setup:** Students will use Computer 2 to load and run the ‘Robot_Attention_Simulation.m’ script.  The script initializes the simulated robot and the visual stimulus display.
2.  **Stimulus Presentation:** The script will display a square target (20mm x 20mm) on the monitor. The target's position will be randomized within the monitor's horizontal field (x-coordinates between 320mm and 680mm) and vertical field (y-coordinates between 240mm and 520mm).
3.  **Attention Weight Adjustment:** Students will use the USB mouse to adjust the attention weight applied to the target's location.  The attention weight is a numerical value (between 0.0 and 1.0) representing the emphasis placed on the target's position. A value of 0.0 means no attention is paid to the target's location, while a value of 1.0 indicates maximal attention.
4.  **Observation:** Students will carefully observe the robot’s response – its activation level – in the MATLAB console. The activation level will fluctuate based on the adjustment of the attention weight.
5.  **Weight Iteration:** Students will systematically adjust the attention weight across the range of 0.0 to 1.0, recording the corresponding activation level in the MATLAB console.  A minimum of 10 distinct attention weight values should be tested.
6.  **Data Recording:** Students will record the attention weight and the corresponding activation level in the data table provided (see Section 6).
7.  **Repeat:**  Repeat the experiment with a different randomized stimulus position.

**6. Data Collection (Template)**

| Attention Weight | Activation Level | Observation Notes (e.g., Rate of change, Plateau effect) |
| ---------------- | ----------------- | ------------------------------------------------------- |
| 0.0              |                   |                                                          |
| 0.1              |                   |                                                          |
| 0.2              |                   |                                                          |
| 0.3              |                   |                                                          |
| 0.4              |                   |                                                          |
| 0.5              |                   |                                                          |
| 0.6              |                   |                                                          |
| 0.7              |                   |                                                          |
| 0.8              |                   |                                                          |
| 0.9              |                   |                                                          |
| 1.0              |                   |                                                          |

**7. Analysis Questions (4 bullets)**

1.  Describe the relationship between the attention weight and the robot’s activation level.  How does increasing the attention weight affect the activation level?
2.  At what point(s) does the robot’s response appear to stabilize? What does this suggest about the FEP and attention minimization?
3.  If the attention weight is set to 0.0, how does the robot’s response differ from when it receives maximal attention?
4.  How does this experiment demonstrate the principle of selective perception and the role of attention in reducing 'surprise'?

**8. Expected Results (Guideline)**

Students should observe that the robot's activation level increases proportionally to the attention weight applied to the target's location. When the attention weight is low (close to 0.0), the activation level will be minimal, reflecting little focus on the target. As the attention weight increases, the activation level will rise, indicating a greater emphasis on the target.  At high attention weights (close to 1.0), the activation level may appear to plateau, reflecting the system's tendency to minimize surprise by focusing on the strongest signal. Students should be able to relate this behavior to the concept of the FEP and the drive to reduce internal 'surprise'.  [INSTRUCTOR] - Monitor student discussion to ensure they connect the activity to the lecture material.