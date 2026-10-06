Hi Class,

We will do the simulated defocus lab in tomorrow's class. Please bring at least 3 objects that contains rich features per group, you're welcome to bring more. Avoid dark objects like a black umbrella. I will walk through basic concepts with you before starting the lab.


Simulated Defocus
Over the next few weeks we cover camera focus and defocus, and projector focus and defocus. A real lens blurs each part of the scene by an amount that depends on its depth. This lab is a hand-crafted way of understanding that: you fake depth-dependent blur with masks.

Take a photo of a scene with many different depths in it, near objects and far ones, and save it as image.jpg at the repository root.

Blur the whole photo with a Gaussian. The blur has two parameters, the kernel size and the standard deviation. This blur is the same everywhere in the image; camera defocus is not, which is the point of the next step.

Make a mask for one depth layer: an image of the same size as the photo, white on the foreground you pick and black everywhere else. Paint it by hand in any image editor, or make it with Segment Anything or, better, from a depth map by Depth Anything. Then show the photo where the mask is white and the blurred photo everywhere else: that layer is in focus, the rest is defocused.

Repeat for three or more layers of the scene, from near to far, with masks mask1.png, mask2.png, … and defocused images defocus1.png, defocus2.png, … Viewed in sequence they give the impression of the camera pulling focus through the scene.

Combine every mask into one image, each layer at its own color. You may use a color map of your choice. Does it look like a depth image? Answer yes or no and say why.

Extra credit (up to 10 points, optional): defocus with no halos and no holes. Blurring the whole photo and masking it leaves a halo of subject colour around the in-focus object; cutting the subject out of the background before blurring leaves a dark fringe instead. Work out why both happen and produce results with neither, as defocus1_clean.png, defocus2_clean.png, …

Implementation: what you did and why, and the files involved.

Demonstration: one clean result beside your step 4 result, and zoomed edge crops side by side with a few sentences on the difference.

Agentic workspace: tell your agent Start Lab 5. It fetches the lab, including the Python starter defocus.py, and tells you what to do next.

Otherwise: use the starter script if you like, defocus.py for Python or defocus.m for MATLAB. Both do steps 2 to 5 once image.jpg and the masks are in place: they write the defocused images and the combined mask masks.png. Your work is the photo and the masks; change the blur if the effect is too weak or too strong.

Submission
Submit one PDF named Lab05.pdf, the two-digit lab number. It shows the photo and the combined mask image, then one subsection per focal plane with its mask and its defocused result, from near to far; a Compositing section describing how the layers were put back together; then your yes-or-no answer with the reason. The Details table asks which tool made the masks. Both templates below have the same sections and are graded the same way. The Observations section is written by a group member, not by an AI; every red underlined placeholder must be filled in, except in the extra credit section.

Agentic workspace: tell your agent Build the PDF. It collects your results into the report, drafts the AI disclosure for your group to confirm, points out anything missing, and produces the ready-to-submit PDF.

Otherwise: fill in the Word template for this lab, Lab5.docx, and export it to PDF.