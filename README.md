Cool Rain Effect

Overview
This project generates a visually satisfying rain effect that interacts with the outline of objects in an image. Inspired by a Twitter GIF, the effect simulates rain hitting an object's silhouette, with droplets flowing down edges dynamically.

Features
•	Upload any image, then an outline will be automatically detected.
•	Generate rain particles that interact with the detected edges.
•	Customize background and rain colors.
•	Mess around with rain setting in the advanced tab.

How It Works
1.	Edge Detection: The image is converted to grayscale, and OpenCV’s Canny edge detection extracts object outlines.
2.	Rain Simulation: Randomly generated rain streaks fall from the top and interact with detected edges.
3.	Dripping Effect: If rain hits an edge, it can either stop, slide along the edge, or drip down based on predefined physics rules.
4.	Customization: Users can modify the rain color, background color, etc.

Tips for Best Results
•	Use high-contrast images for more dramatic effects
•	Experiment with different settings in the Advanced Tab
•	Try various image types to see unique rain outline styles

Installation
1.	Download the ZIP and run the exe.
   
OR

3.	git clone https://github.com/AdnanZXgamer/Cool-Rain-Effect.git

Future Plans (Maybe)
1.  Improve dripping physics for more realism.
2.  Support real-time video processing.

Contributing
Pull requests are welcome! If you have any ideas to enhance the effect, feel free to contribute.

Credits
Created by AdnanZXG

License
This project is open-source and available under the MIT License.


