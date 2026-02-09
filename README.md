🎓 PLANEXA - My AI Floor Plan Generator Project

Hey there! 👋 I'm a computer science student, and this is PLANEXA - a project I built from scratch to learn about AI, web development, and 3D graphics. It's not perfect, but it works and I learned SO much building it!
✨ What This Thing Does

Basically, you tell it:

    How big your building should be

    What rooms you need (bedrooms, kitchen, etc.)

    How many floors you want

And it uses AI magic (well, Graph Neural Networks) to:

    Figure out the best places to put rooms

    Draw a 2D floor plan with colors and labels

    Create a cool 3D view you can spin around

    Let you save it as a PDF or PNG

🧠 Why I Built This

Honestly? I wanted to make something that combined all the stuff I was learning in class:

    AI/ML courses → Graph Neural Networks

    Web Development → Flask, JavaScript

    Computer Graphics → Three.js, SVG

    Algorithms → Room placement optimization

Plus, I've always been fascinated by architecture and wanted to see if I could make a computer design buildings!
🚀 How to Run It (It's Actually Easy!)
Step 1: Get the Code
bash

git clone https://github.com/Achu067/planexa.git
cd planexa

Step 2: Run the Backend
bash

cd backend
python -m venv venv

# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

pip install -r requirements-minimal.txt
python app.py

Step 3: Open the Website

Just open frontend/index.html in your browser! (Or use Chrome, Firefox, etc.)
📚 What I Learned (The Hard Way)
1. AI Is Cool But Tricky

    Graph Neural Networks sound fancy, but making them work for room layouts was HARD

    Had to learn about spatial relationships and adjacency matrices

    Turns out, placing a bathroom next to a kitchen is a bad idea 😅

2. JavaScript Can Do 3D?!

    Three.js blew my mind - you can make 3D graphics in a browser!

    SVG drawing is like HTML but for shapes

    Making things interactive (click, hover, zoom) takes patience

3. Full-Stack Means Everything Breaks Everywhere

    Frontend says: "Backend sent weird data"

    Backend says: "Frontend asked for impossible things"

    Me: cries in console.log()

4. Good Code ≠ Working Code

    My first version worked but was spaghetti code

    Rewrote it 3 times to make it readable

    Comments are your best friend at 3 AM

🔧 The Tech Stack (What I Actually Used)
Frontend (The Pretty Part)

    HTML/CSS/JavaScript - The basics I learned in class

    Three.js - For the 3D building view (so cool!)

    Chart.js - For showing stats and graphs

    SVG - For drawing floor plans

Backend (The Brain)

    Python - My favorite language

    Flask - Simple web framework

    NumPy/NetworkX - Math and graph stuff

    SVGWrite - Making SVG files from Python

AI Stuff (The Magic)

    Graph Algorithms - For room connections

    Spatial Optimization - Making rooms fit nicely

    Rule-based Systems - Where to put windows/doors

💡 Cool Features I'm Proud Of

    Real-time 3D View - You can rotate and zoom the building!

    Smart Room Placement - Bedrooms together, kitchen near entrance

    PDF Export - Makes it look professional

    Multiple Floors - With stairs that actually connect

    Color-coded Rooms - Blue for bedrooms, green for living room, etc.

🎮 How to Use It (For Real)

    Set the size: Like 12m wide × 10m long

    Add rooms: Click "+ Add Room" for each type you need

    Pick a style: Modern, Traditional, Minimalist, or Open Plan

    Click Generate: Watch the AI do its thing!

    Explore: Switch between 2D/3D, check different floors

    Save it: Export as PNG or PDF for your project

🐛 Known Issues (Because It's a Student Project)

    Sometimes rooms overlap - The AI isn't perfect yet

    3D view can be slow on old computers

    Weird room shapes if you pick strange dimensions

    Mobile isn't perfect - Works best on desktop

🏗️ Project Structure (How I Organized It)
text

planexa/
├── frontend/                    # What you see in browser
│   ├── index.html              # Main page
│   ├── style.css               # All the colors and layout
│   └── script.js               *All the magic happens here!*
│
├── backend/                    # Server and AI brain
│   ├── app.py                 *Flask server - connects everything*
│   ├── ml_engine/             # AI algorithms
│   ├── svg_renderer/          # Drawing floor plans
│   └── export_engine/         # Saving as PDF/PNG
│
└── README.md                  # This file!

📖 What Each File Does
frontend/script.js - The Controller

    Listens to your button clicks

    Draws the floor plan with SVG

    Creates the 3D view with Three.js

    Talks to the backend API

backend/app.py - The Server

    Listens for requests from frontend

    Runs the AI algorithms

    Sends back floor plan data

    Handles PDF/PNG export

backend/ml_engine/ - The AI Brain

    gnn_predictor.py - Predicts room layouts

    room_placer.py - Puts rooms in good spots

    furniture_layout.py - Adds beds, sofas, etc.

    window_door_logic.py - Places windows and doors

🎓 How This Helped My Studies
For AI/ML Class:

    Actually implemented GNNs (not just theory!)

    Learned about feature engineering for spatial data

    Understood optimization challenges

For Web Development Class:

    Built a full REST API with Flask

    Made a responsive frontend without frameworks

    Learned about CORS, AJAX, JSON APIs

For Algorithms Class:

    Applied graph algorithms (adjacency, paths)

    Used optimization techniques

    Implemented search algorithms for room placement

For Graphics Class:

    Created 2D graphics with SVG

    Built 3D scenes with Three.js

    Learned about cameras, lighting, materials

🤝 Want to Help Improve It?

If you're also a student (or just nice), you can:

    Find bugs - I'm sure there are many!

    Suggest features - What would make it better?

    Improve the AI - Make smarter room layouts

    Fix my messy code - I'm still learning!

Just:
bash

# Fork it
# Make changes
# Send a pull request

🌟 Future Ideas (If I Have Time)

    VR Mode - Walk through your building in VR!

    Better AI - Learn from real floor plans

    Mobile App - Design on your phone

    More Styles - Victorian, Futuristic, etc.

    Material Calculator - How much wood/cement you need

🙏 Thank You!

To my professors who answered my endless questions
To classmates who tested early (buggy) versions
To Stack Overflow for saving me 1000 times
To coffee for keeping me awake
📞 Contact & Connect

I'm a student looking to learn and grow! Feel free to:

    Email me: student.email@college.edu

    Connect on LinkedIn: Your Name

    Check my GitHub: @yourusername

⚠️ Disclaimer

This is a student project, not a professional tool. Don't use it to design your actual house! 😄
<div align="center">
🎉 Try It Out!

https://img.shields.io/badge/Click_Here-Run_PLANEXA-blue?style=for-the-badge

Remember: Every expert was once a beginner who kept trying.
</div>

Built with ❤️, ☕, and way too many late nights by a computer science student who believes in learning by building.
