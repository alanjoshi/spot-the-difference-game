# Spot The Difference Game

HIT137 Assignment 3 project using Python, Tkinter, and OpenCV.

## Overview

This is a desktop spot-the-difference game. The user loads an image, and the program creates a modified copy with 5 hidden differences. The original image is displayed on the left, and the modified image is displayed on the right. The player clicks on the modified image to find the differences.

## Features

- Loads JPG, PNG, and BMP image files
- Displays original and modified images side by side
- Generates exactly 5 random differences
- Prevents difference regions from overlapping
- Uses OpenCV image processing
- Includes 3 difference types:
  - Colour shift
  - Brightness change
  - Object removal / blur
- Detects player clicks on the modified image
- Draws red circles around correctly found differences
- Tracks remaining differences
- Tracks mistakes, with a maximum of 3 per image
- Shows a game over message after 3 mistakes
- Reveals unfound differences with blue circles
- Tracks cumulative score across images

## Requirements

- Python 3
- OpenCV
- Pillow

Install the required packages:

```bash
pip install opencv-python pillow
```

## How To Run

Run the program from the project folder:

```bash
python main.py
```

or:

```bash
python3 main.py
```

## Project Files

- `main.py`  
  Contains the Tkinter GUI and game controller logic.

- `differences.py`  
  Contains the difference classes and OpenCV image alteration methods.

## OOP Design

The project uses object-oriented programming principles:

- `SpotTheDifferenceGUI` manages the Tkinter interface.
- `GameController` manages game state and user interaction.
- `Difference` is the parent class for all difference types.
- `ColourShiftDifference`, `BrightnessDifference`, and `ObjectRemovalDifference` inherit from `Difference`.
- Each difference type implements its own `apply()` method, demonstrating polymorphism.

## How The Game Works

1. Click **Load Image** and choose an image file.
2. The program creates a modified copy with 5 random differences.
3. Click on the modified image to find differences.
4. Correct clicks are marked with red circles.
5. Wrong clicks increase the mistake counter.
6. After 3 mistakes, the round ends.
7. Click **Reveal Differences** to show any remaining differences in blue.
8. Load another image to continue playing.
