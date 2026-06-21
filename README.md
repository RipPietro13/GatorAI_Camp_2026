# Gator AI Summer Camp 2026

## Introduction

This is a draft repository for the **Gator AI Summer Camp 2026** program. The camp will teach students the basics of AI and how to apply AI to solve real-world problems.

### Program Overview

- **Week 1**: Introduction to Python programming using game development
- **Week 2**: AI concepts and their application to real-world problems

### Game Description

The project features a **top-down adventure game**, similar to The Legend of Zelda. Players will be able to:
- Move around the map
- Collect items  
- Interact with NPCs

### Code Standards

All code in this project should be:
- **Well-documented** with clear comments and docstrings
- Follow **Python best practices** for clean, maintainable code
- **Organized logically** to teach coding principles in order (variables → functions → classes → objects)

---

## Week 1: Introduction to Python Programming 

**Duration**: ~4 hours per day  
**Schedule**: 1 hour morning session + 2 hours afternoon + 1 hour evening with TAs

### Day 1: Python Setup and Game Introduction

**Objective**: Set up programming environment and begin coding fundamentals.

#### Setup Tasks
- **Install & Run IDE**: Explain what IDEs are and set up development environment
- **Install Python**: Walk through Python installation (if not already installed)
- **GitHub Setup**: Sign-in or sign-up for GitHub account
- **Download Project**: Clone from [Ian's GitHub Repository](https://github.com/UFResearchComputing/GatorAI_Camp_2026)
- **Hello World**: Demonstrate running "Hello, World!" in a Python script

#### Core Concepts
- **Basic Python Syntax**
  - Simple print statements and comments
  - Indentation rules in Python
- **Libraries and Importing**: Explain how to import and use external libraries
- **Game Environment Overview**
  - Introduce existing game framework
  - Show game file locations and how to run the game
- **Variables & Data Types (Basic)**
  - Integers, floats, strings
  - Assign simple values (character names, positions, etc.)

#### Exercise: Customize a Splash Screen
- Modify "Hello, World!" splash screen to display welcome message
- Use variables to store player name or game title
- **Deliverable**: Push project to personal GitHub repository

---

### Day 2: Sprites and Game Logic

**Objective**: Explore game mechanics and make active changes to game code.

#### Core Concepts
- **Loading Character Sprites**
  - Import image files (PNGs, JPGs) into game code
  - Position sprites on screen
- **Basic Conditionals**
  - `if` statements for simple conditions
  - Examples: button presses, health checks
- **Simple Functions**
  - Create functions like `move_character()` 
  - Demonstrate code organization benefits

#### Exercise: Adding Your First Character
- Add a single character sprite to the game
- Use [Piskel](https://www.piskelapp.com/) to create unique sprites
- Experiment with character position and appearance
- **Deliverable**: Push project to personal GitHub repository

---

### Day 3: Dialogue Trees and Interactions

**Objective**: Create branching conversations and interactive dialogue systems.

#### Core Concepts
- **Introduction to Dialogue Trees**
  - Branching conversation options
  - Store dialogue in data structures (lists/dictionaries)
- **Using Lists or Dictionaries (Basic)**
  
  Example dictionary approach:
  ```python
  dialogue = { 
    "greeting": "Hello, traveler!", 
    "option1": "Where am I?", 
    "option2": "Who are you?" 
  }
  ```
- **Loops for Navigating Dialogue**
  - `for` loops to cycle through dialogue options
  - Conditionals for conversation branching

#### Exercise: Implementing a Basic Conversation
- Give newly added sprite a short conversation
- Use `input()` for dialogue selection and response branching
- **Deliverable**: Push project to personal GitHub repository

---

### Day 4: Advanced Dialogue and Debugging

**Objective**: Enhance dialogue systems, add sprite interactions, and learn debugging techniques.

#### Core Concepts
- **Refining Dialogue Trees**
  - Multi-step dialogue structures
  - Explain this as the original "AI"
- **Sprite Interaction**
  - Tie sprite actions to dialogue choices
  - Change expressions based on conversation branches
  - Sprite movement (walking away, disappearing)
- **Basic Debugging & Code Organization**
  - Using `print()` statements to track variables
  - Common syntax errors and how to read error messages
  - Organizing dialogue code in separate files/functions

#### Exercise: Complex Dialogue
- Create multi-branch dialogue for character
- **Optional**: Group brainstorming for final projects
- **Deliverable**: Push project to personal GitHub repository

---

### Day 5: Project Finalization and Presentations

**Objective**: Polish game modifications and present final projects.

#### Activities
- **Polish & Personalization**
  - Add custom sprites, dialogue branches, animations
- **Testing**
  - Test all dialogue paths and sprite interactions
  - Use checklist approach: sprite display, dialogue functionality
- **Show & Tell**
  - Demonstrate modified games
  - Highlight added characters and dialogue systems
- **Reflection & Next Steps**
  - Group discussion: Python learnings and challenges
  - Review group projects (additional characters, scenes, menus)
- **Deliverable**: Push final project to personal GitHub repository

---

## Week 2: Introduction to Artificial Intelligence

### Day 1: AI Concepts and Environment Setup

**Objective**: Learn AI fundamentals and prepare development environment.

#### Core Concepts
- **Show Week Plan**: Overview of full week schedule
- **What Is AI/ML?**
  - Differentiate AI, Machine Learning, and Deep Learning
  - Real-world applications (image recognition, chatbots, etc.)
- **Facial Recognition Overview**
  - Face detection vs. recognition vs. expression recognition
  - Introduction to libraries (OpenCV, face_recognition)
- **Setting Up AI Environment**
  - Install Python libraries (`opencv-python`, `face_recognition`)
  - Discuss CPU/GPU considerations or use Google Colab
- **Data Gathering & Model Training Basics**
  - Using images/webcam for training/fine-tuning
  - Dataset labeling, data requirements
  - **Ethical considerations**: privacy, consent

#### Hands-On Exercise
- Verify AI library installations (`pip install opencv-python`)
- **Optional**: Test script for face detection from webcam/image

---

### Day 2: Facial Recognition Model Training

**Objective**: Learn model training concepts and implement expression recognition.

#### Core Concepts
- **Model Training Fundamentals**
  - Training vs. validation vs. test data
  - Small dataset of facial expressions (happy, sad, neutral)
  - Students capture labeled images
- **Implementing Training Pipeline**
  - Code walkthrough for training/fine-tuning expression models
  - Focus on understanding how models learn from data
- **Testing & Evaluating Models**
  - Run model on test images
  - Print accuracy and confusion matrix
- **Saving Models**
  - Save trained model to file (`.h5` or `.pkl`)
  - Loading models for game integration

#### Hands-On Exercise
- Follow guided notebook/script to train expression recognition model
- Test on personal images or sample photos
- Check and discuss accuracy results

---

### Day 3: Large Language Models and APIs

**Objective**: Understand LLMs and integrate them via API calls.

#### Core Concepts
- **Overview of Large Language Models (LLMs)**
  - What LLMs are and how they're trained
  - Natural language response capabilities
  - Common providers (OpenAI, Hugging Face, etc.)
- **API Setup**
  - Obtain API keys (instructor-guided)
  - Basic Python script for LLM endpoint requests
  - Using `requests` library or official client libraries
- **Handling LLM Responses**
  - Parse JSON/text responses
  - Understanding token usage and limits

#### Hands-On Exercise
- Write Python script to send prompts to LLM
- Print console responses
- Generate dialogue lines or short stories
- Use original dialogue as context pre-prompts

---

### Day 4: Game Integration - Facial Recognition + LLM

**Objective**: Combine facial recognition and LLM technologies in the game.

#### Core Concepts
- **Loading Facial Recognition Model**
  - Load saved model from Day 2 into game code
  - Integrate webcam/image capture for real-time analysis
  - Snapshot-based approach (keypress to check expression)
- **API Calls from In-Game**
  - Combine LLM API script with game logic
  - Dynamic prompts based on recognized expressions
  - Example: "User is smiling. NPC responds with friendly greeting."
- **Designing Interaction Flow**
  - Craft LLM prompts with contextual info
  - Map expressions to conversation branches (happy → friendly, sad → consoling)
- **Error Handling & Debugging**
  - Handle API downtime or recognition failures
  - Use `print()` statements for debugging

#### Hands-On Exercise
- Incorporate model + LLM calls into game dialogue function
- Group testing: one person as "player" (webcam), other monitors code

---

### Day 5: Final Demonstrations and Reflection

**Objective**: Complete AI-enhanced projects and present to group.

#### Activities
- **Polish & Prepare**
  - Refine dialogue flows and sprite reactions
  - Add more expression-to-prompt logic
- **Presentation of AI-Enhanced NPCs**
  - Demonstrate expression recognition (smile, frown, etc.)
  - Show LLM-generated dialogue responses
- **Discussion & Troubleshooting**
  - Group discussion: successes, challenges, real-world AI considerations
  - Topics: scale, bias, privacy, ethics
- **Next Steps & Further Learning**
  - Areas for exploration: reinforcement learning, advanced computer vision, complex game design
  - Work on group projects as time allows
- **Final Reflection**
  - Share one AI learning, one challenge, one future interest area
  - **Optional**: Feedback forms or understanding quizzes

---

## Resources

- [Python Documentation](https://docs.python.org/3/)
- Sprite Sheet Editor: [Piskel](https://www.piskelapp.com/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [GitHub Desktop](https://desktop.github.com/) (for easier Git management)

## Technical Requirements

### Python Libraries
```bash
pip install pygame
pip install opencv-python
pip install requests
# Additional libraries as needed for specific AI frameworks
```

### Hardware Recommendations
- **Minimum**: 4GB RAM, integrated graphics
- **Recommended**: 8GB+ RAM, dedicated graphics card for AI processing
- **Webcam**: Required for facial recognition exercises

## Attribution

- Game art assets from [OpenGameArt.org](https://opengameart.org/), licensed under CC0 1.0 Universal (CC0 1.0) Public Domain Dedication. Author: ArMM1998
- Educational framework inspired by game-based learning methodologies

## Contributing

This is an educational repository. Contributions should focus on:
- Improving code clarity and documentation
- Adding beginner-friendly examples
- Enhancing learning progressions
- Fixing bugs or compatibility issues

## License

This project is intended for educational use. Please respect the licensing terms of all included assets and libraries.
