import tkinter as tk
import random

# Constants
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
COLORS = ["red", "blue", "yellow"]
SIZES = [20, 40, 60]  # Doubled sizes for canvas balls
CONTROL_PANEL_SCALE = 1.5  # 1.5x size increase for control panel circles
SPEED_INCREMENT = 2

class BallAnimationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ball Animation")
        
        # Canvas
        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="lightgray")
        self.canvas.pack()

        # Control Panel
        self.control_panel = tk.Frame(root, bg="white", height=200)
        self.control_panel.pack(fill=tk.X)

        # Combined Size and Color Selection
        self.selection_canvas = tk.Canvas(self.control_panel, width=400, height=200, bg="white", highlightthickness=0)
        self.selection_canvas.grid(row=0, column=0, padx=10, pady=5, sticky="n")

        # Size Selection (Upper Part)
        x_offset = 50  # Initial X offset for circles
        self.size_var = tk.IntVar(value=0)  # Default size is not selected
        self.size_circles = {}

        for size in SIZES:
            scaled_size = int(size * CONTROL_PANEL_SCALE)  # Scale size by 1.5x
            circle = self.selection_canvas.create_oval(
                x_offset - scaled_size // 2, 50 - scaled_size // 2, 
                x_offset + scaled_size // 2, 50 + scaled_size // 2,
                fill="gray", outline="black", width=2
            )
            self.size_circles[circle] = size
            self.selection_canvas.tag_bind(circle, "<Button-1>", lambda event, s=size: self.select_size(s))
            x_offset += 120  # Space between circles

        # Add vertical space between size and color selection
        vertical_gap = 40  # Gap of 40 units between size and color selection

        # Color Selection (Lower Part)
        x_offset = 50  # Initial X offset for squares
        self.color_var = tk.StringVar(value="")  # Default color is not selected
        self.color_rectangles = {}
        self.current_animation = None  # To track the current animated rectangle

        for color in COLORS:
            square = self.selection_canvas.create_rectangle(
                x_offset - 20, vertical_gap + 80 - 20, x_offset + 20, vertical_gap + 80 + 20,
                fill=color, outline="black"
            )
            self.color_rectangles[square] = color
            self.selection_canvas.tag_bind(square, "<Button-1>", lambda event, c=color, r=square: self.select_color(c, r))
            x_offset += 120  # Space between squares

        # Buttons
        self.button_frame = tk.Frame(self.control_panel, bg="white")
        self.button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        tk.Button(self.button_frame, text="START", bg="red", command=self.start_animation, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="STOP", bg="blue", command=self.stop_animation, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="RESET", bg="yellow", command=self.reset_canvas, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Speed Up", command=self.speed_up, width=10).pack(side=tk.LEFT, padx=5)

        # Variables
        self.balls = []  # List of ball objects
        self.is_running = False
        self.speed_multiplier = 1
        self.selected_color_rect = None

    def select_size(self, size):
        """Sets the selected size."""
        self.size_var.set(size)

        # Automatically add a ball if a color is already selected
        if self.color_var.get():
            self.add_ball()

    def select_color(self, color, rectangle):
        """Sets the selected color and starts an animation on the selected rectangle."""
        self.color_var.set(color)

        # Stop animation on previous rectangle
        if self.current_animation is not None:
            self.selection_canvas.itemconfig(self.current_animation, fill=self.color_rectangles[self.current_animation])
            self.root.after_cancel(self.animation_job)  # Cancel previous animation

        # Start animation on the new rectangle
        self.current_animation = rectangle
        self.animate_rectangle(rectangle)

    def animate_rectangle(self, rectangle):
        """Creates a blinking effect on the selected rectangle."""
        current_fill = self.selection_canvas.itemcget(rectangle, "fill")
        new_fill = "white" if current_fill != "white" else self.color_rectangles[rectangle]
        self.selection_canvas.itemconfig(rectangle, fill=new_fill)
        self.animation_job = self.root.after(500, lambda: self.animate_rectangle(rectangle))  # Loop animation

    def add_ball(self):
        """Adds a ball with the selected size and color at a random position."""
        size = self.size_var.get()
        color = self.color_var.get()

        # Ensure both size and color are selected
        if size and color:
            x = random.randint(size, CANVAS_WIDTH - size)
            y = random.randint(size, CANVAS_HEIGHT - size)
            dx, dy = random.choice([-1, 1]) * random.randint(1, 5), random.choice([-1, 1]) * random.randint(1, 5)
            ball_id = self.canvas.create_oval(x - size, y - size, x + size, y + size, fill=color)
            self.balls.append({"id": ball_id, "dx": dx, "dy": dy, "size": size})

            # Reset selection after adding the ball
            self.reset_selection()

    def reset_selection(self):
        """Resets the color and size selection to default values."""
        self.size_var.set(0)  # Reset size to unselected
        self.color_var.set("")  # Reset color to unselected

        # Stop any ongoing animation
        if self.current_animation is not None:
            self.selection_canvas.itemconfig(self.current_animation, fill=self.color_rectangles[self.current_animation])
            self.root.after_cancel(self.animation_job)
            self.current_animation = None

    def move_balls(self):
        """Animates the balls."""
        if not self.is_running:
            return
        
        for ball in self.balls:
            x1, y1, x2, y2 = self.canvas.coords(ball["id"])
            dx, dy = ball["dx"], ball["dy"]
            
            # Check for collisions with canvas edges
            if x1 + dx < 0 or x2 + dx > CANVAS_WIDTH:
                ball["dx"] = -dx  # Reverse X direction
            if y1 + dy < 0 or y2 + dy > CANVAS_HEIGHT:
                ball["dy"] = -dy  # Reverse Y direction
            
            # Move ball
            self.canvas.move(ball["id"], ball["dx"] * self.speed_multiplier, ball["dy"] * self.speed_multiplier)
        
        # Continue animation
        self.root.after(20, self.move_balls)
    
    def start_animation(self):
        """Starts the animation."""
        if not self.is_running:
            self.is_running = True
            self.move_balls()
    
    def stop_animation(self):
        """Stops the animation."""
        self.is_running = False
    
    def reset_canvas(self):
        """Resets the canvas, removing all balls."""
        self.is_running = False
        self.canvas.delete("all")
        self.balls.clear()
        self.speed_multiplier = 1  # Reset speed
    
    def speed_up(self):
        """Increases the speed of the balls."""
        self.speed_multiplier += SPEED_INCREMENT

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = BallAnimationApp(root)
    root.mainloop()
