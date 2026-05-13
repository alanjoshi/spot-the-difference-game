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
