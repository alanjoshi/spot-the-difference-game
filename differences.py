import cv2
import random
import numpy as np

class Difference:
    """
    Base Class (Parent Class) for all difference types.
    This demonstrates Inheritance and Polymorphism.
    """
    def __init__(self, x, y, width, height):
        """
        Constructor - Initializes a difference region.
        
        Args:
            x, y: Top-left corner coordinates
            width, height: Size of the difference region
        """
        # Encapsulation: Using protected attributes (_)
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._found = False

    def apply(self, image):
        """Abstract method - Must be implemented by child classes"""
        raise NotImplementedError("Child classes must implement the apply() method")

    def is_clicked(self, click_x, click_y, tolerance=25):
        """
        Checks if a player's click is close enough to this difference.
        
        Returns:
            bool: True if click is within tolerance distance
        """
        center_x = self._x + self._width // 2
        center_y = self._y + self._height // 2
        distance = ((click_x - center_x)**2 + (click_y - center_y)**2) ** 0.5
        return distance <= tolerance

    def mark_as_found(self):
        """Mark this difference as found by the player"""
        self._found = True

    def is_found(self):
        """Check if this difference has been found"""
        return self._found

    def get_center(self):
        """Returns the center point of the difference region"""
        return (self._x + self._width//2, self._y + self._height//2)


class ColourShiftDifference(Difference):
    """
    Child Class 1: Changes the color (hue) in a region.
    Demonstrates Inheritance and Polymorphism.
    """
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)   # Call parent constructor
        self._hue_shift = random.randint(16, 32)  # Noticeable but still natural

    def apply(self, image):
        roi = image[self._y:self._y+self._height,
                    self._x:self._x+self._width]

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        hsv[:, :, 0] = (hsv[:, :, 0] + self._hue_shift) % 180
        shifted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        tint_colour = np.array(
            random.choice([(45, 80, 255), (255, 140, 60), (80, 220, 80)]),
            dtype=np.uint8
        )
        tint = np.full_like(roi, tint_colour)
        image[self._y:self._y+self._height,
              self._x:self._x+self._width] = cv2.addWeighted(shifted, 0.84, tint, 0.16, 0)
        


class BrightnessDifference(Difference):
    """
    Child Class 2: Changes the brightness of a region.
    """
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._brightness_change = random.choice([
            random.randint(-65, -40),
            random.randint(30, 55)
        ])

    def apply(self, image):
        """Apply brightness adjustment"""
        roi = image[self._y:self._y+self._height,
                    self._x:self._x+self._width].astype(np.int16)
        adjusted = np.clip(roi + self._brightness_change, 0, 255).astype(np.uint8)
        image[self._y:self._y+self._height,
              self._x:self._x+self._width] = adjusted


class ObjectRemovalDifference(Difference):
    """
    Child Class 3: Removes a small object/region.
    """

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

    def apply(self, image):
        """
        Apply subtle object removal effect.
        """

        roi = image[self._y:self._y+self._height,
                    self._x:self._x+self._width]

        kernel = max(15, min(self._width, self._height) // 2)
        if kernel % 2 == 0:
            kernel += 1

        blurred = cv2.GaussianBlur(roi, (kernel, kernel), 0)
        softened = cv2.addWeighted(blurred, 0.91, np.full_like(roi, 245), 0.09, 0)

        image[self._y:self._y+self._height,
            self._x:self._x+self._width] = softened
