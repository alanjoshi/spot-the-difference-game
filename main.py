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
            self.btn_reveal.config(state=tk.NORMAL)

            # =====================================================================
# Test/Integration reference code for members doing Part 3 and Part 4
# =====================================================================
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
        self.difference_classes = [
            ColourShiftDifference,
            BrightnessDifference,
            ObjectRemovalDifference
        ]    
    def load_new_game(self, filepath):
        # Load image
        self.original_img = cv2.imread(filepath)
        if self.original_img is None:
            print("ERROR: Image not loaded properly")
            return
    
        self.modified_img = self.original_img.copy()
        self.display_img = self.modified_img.copy()

        # Reset state
        self.difference_regions = []
        self.found_regions = []
        self.mistakes = 0
        self.score = 0

        height, width, _ = self.original_img.shape

        # Generate 5 non-overlapping regions
        for _ in range(5):
            while True:
                w, h = 80, 80
                x = random.randint(0, width - w)
                y = random.randint(0, height - h)

                new_region = (x, y, w, h)

                overlap = False
                for region in self.difference_regions:
                        rx = region._x
                        ry = region._y
                        rw = region._width
                        rh = region._height
                        if (x < rx + rw and x + w > rx and
                            y < ry + rh and y + h > ry):
                            overlap = True
                            break

                if not overlap:
                    break

            

            # Randomly choose a difference class
            DiffClass = random.choice(self.difference_classes)

            # Create difference object
            diff = DiffClass(x, y, w, h)

            # Apply difference
            diff.apply(self.modified_img)
            diff.apply(self.display_img)

            self.difference_regions.append(diff)


            
            

        # Update GUI
        self.gui.update_images(self.original_img, self.display_img)
        self.gui.update_stats(remaining=5, mistakes=0, score=0)

    def handle_click(self, x, y):
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
                self.found_regions.append(region)
                self.score += 10

                cx, cy = region.get_center()


                cv2.circle(self.display_img, (cx, cy), 30, (0, 255, 0), 3)
                cv2.circle(self.original_img, (cx, cy), 30, (0, 255, 0), 3)
                break

        if not correct:
            self.mistakes += 1

        remaining = 5 - len(self.found_regions)

        self.gui.update_images(self.original_img, self.display_img)
        self.gui.update_stats(remaining, self.mistakes, self.score)

        # Lose condition
        if self.mistakes >= 3:
            self.reveal_differences()
            self.gui.show_message("Game Over", "Too many mistakes!", game_over=True)

        # Win condition
        elif remaining == 0:
            self.gui.show_message("You Win!", "You found all differences!", game_over=True)

    def reveal_differences(self):
        if self.display_img is None:
            return   
        for region in self.difference_regions:
            if region in self.found_regions:
                continue

            cx, cy = region.get_center()

            cv2.circle(self.display_img, (cx, cy), 30, (255, 0, 0), 3)
            cv2.circle(self.original_img, (cx, cy), 30, (255, 0, 0), 3)

        self.gui.update_images(self.original_img, self.display_img)

if __name__ == "__main__":
    app = GameController()
    app.gui.mainloop()