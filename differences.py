import cv2
import random

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
        self._hue_shift = random.randint(60, 120)  # Random color shift

    def apply(self, image):
        roi = image[self._y:self._y+self._height,
                    self._x:self._x+self._width]

        roi[:, :, 1] = cv2.add(roi[:, :, 1], 60)
        


class BrightnessDifference(Difference):
    """
    Child Class 2: Changes the brightness of a region.
    """
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._brightness_change = random.randint(-70, -70)  # Slightly darker

    def apply(self, image):
        """Apply brightness adjustment"""
        roi = image[self._y:self._y+self._height, self._x:self._x+self._width].copy()
        image[self._y:self._y+self._height, self._x:self._x+self._width] = cv2.add(roi, self._brightness_change)


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

        blurred = cv2.GaussianBlur(roi, (21, 21), 0)

        image[self._y:self._y+self._height,
            self._x:self._x+self._width] = blurred