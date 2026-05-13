import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import random
from differences import ColourShiftDifference, BrightnessDifference, ObjectRemovalDifference

class SpotTheDifferenceGUI(tk.Tk):
    """
    Main GUI Class for the Spot the Difference Game.
    Inherits from tk.Tk to demonstrate OOP inheritance.
    """
    def __init__(self, game_controller):
        super().__init__()
        
        # Encapsulated attributes
        self._game_controller = game_controller
        self._left_photo = None  # To keep reference to image and avoid garbage collection
        self._right_photo = None
        
        # Window Setup
        self.title("HIT137 - Spot The Difference")
        self.geometry("1200x700")
        self.configure(padx=20, pady=20)
        
        self._build_ui()

    def _build_ui(self):
        """Constructs the Tkinter widgets and layout."""
        # --- Top Frame: Controls & Stats ---
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 20))
        
        # Buttons
        self.btn_load = ttk.Button(control_frame, text="Load Image", command=self._on_load_clicked)
        self.btn_load.pack(side=tk.LEFT, padx=5)
        
        self.btn_reveal = ttk.Button(control_frame, text="Reveal Differences", command=self._on_reveal_clicked, state=tk.DISABLED)
        self.btn_reveal.pack(side=tk.LEFT, padx=5)
        
        # Status Labels
        self.lbl_score = ttk.Label(control_frame, text="Total Score: 0", font=("Arial", 12, "bold"))
        self.lbl_score.pack(side=tk.RIGHT, padx=15)
        
        self.lbl_mistakes = ttk.Label(control_frame, text="Mistakes: 0/3", font=("Arial", 12, "bold"), foreground="red")
        self.lbl_mistakes.pack(side=tk.RIGHT, padx=15)
        
        self.lbl_remaining = ttk.Label(control_frame, text="Remaining: 0", font=("Arial", 12, "bold"), foreground="blue")
        self.lbl_remaining.pack(side=tk.RIGHT, padx=15)

        # --- Middle Frame: Image Display ---
        image_frame = ttk.Frame(self)
        image_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Original Image (Left) - Display only
        self.lbl_orig_img = ttk.Label(image_frame, text="Original Image\n(Load an image to start)", background="lightgray", anchor="center")
        self.lbl_orig_img.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Modified Image (Right) - Clickable
        self.lbl_mod_img = ttk.Label(image_frame, text="Modified Image\n(Click here to spot differences)", background="lightgray", anchor="center")
        self.lbl_mod_img.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Bind the click event ONLY to the modified image
        self.lbl_mod_img.bind("<Button-1>", self._on_image_clicked)

    # --- Event Handlers (Passing input to Game Logic) ---
    
    def _on_load_clicked(self):
        """Handles file selection and passes the path to the game controller."""
        filepath = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if filepath:
            self._game_controller.load_new_game(filepath)
            self.btn_reveal.config(state=tk.NORMAL)

    def _on_reveal_clicked(self):
        """Tells the game logic to reveal answers."""
        self._game_controller.reveal_differences()
        self.btn_reveal.config(state=tk.DISABLED)

    def _on_image_clicked(self, event):
        """Captures x,y coordinates of the click and sends them to Game Logic."""
        # Only process clicks if an image is actually loaded
        if self._right_photo is not None:
            self._game_controller.handle_click(event.x, event.y)

    # --- UI Update Methods (Called by Game Logic) ---
    
    def update_images(self, cv_img_orig, cv_img_mod):
        """
        Converts OpenCV BGR images to Tkinter PhotoImages and displays them.
        This must be called by the Game Logic whenever a circle is drawn.
        """
        # Convert BGR (OpenCV) to RGB (PIL)
        orig_rgb = cv2.cvtColor(cv_img_orig, cv2.COLOR_BGR2RGB)
        mod_rgb = cv2.cvtColor(cv_img_mod, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_orig = Image.fromarray(orig_rgb)
        pil_mod = Image.fromarray(mod_rgb)
        
        # Resize to fit the UI nicely while maintaining aspect ratio (optional but recommended)
        # Assuming a display width of about 550px per image
        pil_orig.thumbnail((550, 550))
        pil_mod.thumbnail((550, 550))
        self.display_width = pil_mod.width
        self.display_height = pil_mod.height
        label_w = self.lbl_mod_img.winfo_width()
        label_h = self.lbl_mod_img.winfo_height()

        self.offset_x = (label_w - self.display_width) // 2
        self.offset_y = (label_h - self.display_height) // 2
        
        # Convert to ImageTk
        self._left_photo = ImageTk.PhotoImage(pil_orig)
        self._right_photo = ImageTk.PhotoImage(pil_mod)
        
        # Update Labels
        self.lbl_orig_img.configure(image=self._left_photo, text="")
        self.lbl_mod_img.configure(image=self._right_photo, text="")

    def update_stats(self, remaining, mistakes, score):
        """Updates the text on the status labels."""
        self.lbl_remaining.config(text=f"Remaining: {remaining}")
        self.lbl_mistakes.config(text=f"Mistakes: {mistakes}/3")
        self.lbl_score.config(text=f"Total Score: {score}")

    def show_message(self, title, message, game_over=False):
        """Displays a pop-up dialog for win/lose conditions."""
        messagebox.showinfo(title, message)
        if game_over:
            self.btn_reveal.config(state=tk.DISABLED)

class GameController:
    def __init__(self):
        self.gui = SpotTheDifferenceGUI(self)
        # Game state
        self.original_img = None
        self.modified_img = None
        self.display_img = None

        self.difference_regions = []
        self.found_regions = []

        self.mistakes = 0
        self.score = 0
        self.game_locked = False
        self.difference_classes = [
            ColourShiftDifference,
            BrightnessDifference,
            ObjectRemovalDifference
        ]

    def load_new_game(self, filepath):
        # Load image
        self.original_img = cv2.imread(filepath)
        if self.original_img is None:
            self.gui.show_message("Load Error", "Image not loaded properly.")
            return
    
        self.modified_img = self.original_img.copy()
        self.display_img = self.modified_img.copy()

        # Reset state
        self.difference_regions = []
        self.found_regions = []
        self.mistakes = 0
        self.game_locked = False

        height, width, _ = self.original_img.shape
        if width < 120 or height < 120:
            self.gui.show_message("Image Too Small", "Please choose an image at least 120 x 120 pixels.")
            return

        # Generate 5 non-overlapping regions
        attempts = 0
        while len(self.difference_regions) < 5 and attempts < 1000:
            attempts += 1
            min_w = max(40, width // 12)
            max_w = max(min_w, min(110, width // 6))
            min_h = max(40, height // 12)
            max_h = max(min_h, min(110, height // 6))
            w = random.randint(min_w, max_w)
            h = random.randint(min_h, max_h)
            x = random.randint(0, width - w)
            y = random.randint(0, height - h)

            overlap = False
            for region in self.difference_regions:
                rx = region._x
                ry = region._y
                rw = region._width
                rh = region._height
                padding = 12
                if (x < rx + rw + padding and x + w + padding > rx and
                    y < ry + rh + padding and y + h + padding > ry):
                    overlap = True
                    break

            if overlap:
                continue

            if len(self.difference_regions) < len(self.difference_classes):
                DiffClass = self.difference_classes[len(self.difference_regions)]
            else:
                DiffClass = random.choice(self.difference_classes)
            diff = DiffClass(x, y, w, h)
            diff.apply(self.modified_img)
            diff.apply(self.display_img)
            self.difference_regions.append(diff)

        if len(self.difference_regions) < 5:
            self.gui.show_message("Region Error", "Could not create 5 non-overlapping differences. Try a larger image.")
            return

        # Update GUI
        self.gui.update_images(self.original_img, self.display_img)
        self.gui.update_stats(remaining=5, mistakes=0, score=self.score)

    def handle_click(self, x, y):
        if self.game_locked:
            return
        if self.mistakes >= 3:
            return
        if self.display_img is None:
            return

        # Adjust scaling (because GUI resizes image)
        img_h, img_w, _ = self.display_img.shape
        disp_w = self.gui.display_width
        disp_h = self.gui.display_height

        scale_x = img_w / disp_w
        scale_y = img_h / disp_h
        # adjust for offset
        x = x - self.gui.offset_x
        y = y - self.gui.offset_y

        # ignore clicks outside image
        if x < 0 or y < 0 or x > self.gui.display_width or y > self.gui.display_height:
            return

        real_x = int(x * scale_x)
        real_y = int(y * scale_y)

        correct = False

        for region in self.difference_regions:
            if region in self.found_regions:
                continue
            # Use Difference class click detection
            if region.is_clicked(real_x, real_y, tolerance=40):
                correct = True
                region.mark_as_found()
                self.found_regions.append(region)
                self.score += 10

                cx, cy = region.get_center()
                radius = max(region._width, region._height) // 2

                cv2.circle(self.display_img, (cx, cy), radius, (0, 0, 255), 3)
                cv2.circle(self.original_img, (cx, cy), radius, (0, 0, 255), 3)
                break

        if not correct:
            self.mistakes += 1

        remaining = 5 - len(self.found_regions)

        self.gui.update_images(self.original_img, self.display_img)
        self.gui.update_stats(remaining, self.mistakes, self.score)

        # Lose condition
        if self.mistakes >= 3:
            self.game_locked = True
            self.gui.btn_reveal.config(state=tk.DISABLED)
            found = len(self.found_regions)
            self.gui.show_message(
                "Game Over",
                f"Too many mistakes! You found {found} out of 5 differences. Load a new image to restart.",
                game_over=True
            )

        # Win condition
        elif remaining == 0:
            self.game_locked = True
            self.gui.show_message("You Win!", "You found all differences! Load a new image to continue.", game_over=True)

    def reveal_differences(self):
        if self.display_img is None:
            return
        self.game_locked = True
        for region in self.difference_regions:
            if region in self.found_regions:
                continue
            region.mark_as_found()
            self.found_regions.append(region)

            cx, cy = region.get_center()
            radius = max(region._width, region._height) // 2

            cv2.circle(self.display_img, (cx, cy), radius, (255, 0, 0), 3)
            cv2.circle(self.original_img, (cx, cy), radius, (255, 0, 0), 3)

        self.gui.update_images(self.original_img, self.display_img)
        self.gui.update_stats(remaining=0, mistakes=self.mistakes, score=self.score)
        self.gui.btn_reveal.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = GameController()
    app.gui.mainloop()
