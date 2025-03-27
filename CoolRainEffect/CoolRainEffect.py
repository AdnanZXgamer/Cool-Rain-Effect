#hi :)
import cv2
import numpy as np
import pygame
import random
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, ttk


class RainParticle:
    def __init__(self, x, y, speed, color, wind_force=None, drip_probability=None):
        self.x = x
        self.y = y
        self.prev_y = y
        self.prev_x = x
        self.speed = speed
        self.color = color
        self.stuck = False
        self.alpha = 255
        self.dripping = False
        self.streak_length = random.randint(5, 15)

        self.wind_force = wind_force if wind_force is not None else random.uniform(0.5, 2.0)
        self.drip_probability = drip_probability if drip_probability is not None else 0.4
        self.drip_speed = random.uniform(1, 3)

    def update(self, edges):
        if not self.stuck:
            self.prev_y = self.y
            self.prev_x = self.x

            wind_x_offset = self.wind_force * 0.2
            next_x = self.x + wind_x_offset
            next_y = self.y + self.speed

            x, y = int(next_x), int(next_y)

            if 0 <= y < edges.shape[0] and 0 <= x < edges.shape[1]:
                if edges[y, x] > 0:
                    self.x = x
                    self.y = y
                    self.stuck = True
                    self.dripping = random.random() < self.drip_probability
                    return

            self.x = next_x
            self.y = next_y
        elif self.dripping:
            self.prev_y = self.y
            self.y += self.drip_speed

            if self.y - self.prev_y > self.streak_length:
                self.dripping = False
                self.alpha = max(0, self.alpha - 50)
        else:
            self.alpha = max(0, self.alpha - 2)

    def draw(self, surface):
        if not self.stuck:
            pygame.draw.line(surface, (*self.color, self.alpha),
                             (int(self.prev_x), int(self.prev_y)),
                             (int(self.x), int(self.y)), 2)
        elif self.dripping:
            pygame.draw.line(surface, (*self.color, self.alpha),
                             (int(self.x), int(self.y - self.streak_length)),
                             (int(self.x), int(self.y)), 2)
        else:
            pygame.draw.circle(surface, (*self.color, self.alpha),
                               (int(self.x), int(self.y)), 2)


class RainEffect:
    def __init__(self, image_path, bg_color=(0, 0, 0), rain_color=(255, 0, 0),
                 max_particles=7000, wind_speed=1.0, wind_randomness=0.5,
                 drip_probability=0.4, particle_speed=15):
        self.original_image = cv2.imread(image_path)

        if self.original_image is None or self.original_image.size == 0:
            raise ValueError("Unable to read the image. The file may be corrupted or not a valid image.")

        pygame.init()
        infoObject = pygame.display.Info()
        screen_width = infoObject.current_w
        screen_height = infoObject.current_h

        height, width = self.original_image.shape[:2]

        scale_width = (screen_width * 0.9) / width
        scale_height = (screen_height * 0.9) / height
        scale = min(1, min(scale_width, scale_height))

        new_width = int(width * scale)
        new_height = int(height * scale)
        self.original_image = cv2.resize(self.original_image, (new_width, new_height),
                                         interpolation=cv2.INTER_AREA)

        self.edges = self.process_image()

        if self.edges is None or self.edges.size == 0:
            raise ValueError("Could not process image edges.")

        self.width = self.edges.shape[1]
        self.height = self.edges.shape[0]

        self.screen = pygame.display.set_mode((self.width, self.height),
                                              pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
        icon = pygame.image.load("icon.ico")
        pygame.display.set_icon(icon)
        pygame.display.set_caption('Rain Effect')

        self.edge_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.edge_surface.fill((0, 0, 0, 0))

        self.bg_color = bg_color
        self.rain_color = rain_color

        self.max_particles = max_particles
        self.wind_speed = wind_speed
        self.wind_randomness = wind_randomness
        self.drip_probability = drip_probability
        self.particle_speed = particle_speed

        self.particles = []
        self.running = False
        self.clock = pygame.time.Clock()
        self.target_fps = 60

        self.particle_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def process_image(self):
        try:
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            edges = cv2.Canny(blurred, 50, 150)
            kernel = np.ones((2, 2), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=2)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            outer_edges = np.zeros_like(edges)
            cv2.drawContours(outer_edges, contours, -1, 255, 1)
            return outer_edges
        except Exception as e:
            raise ValueError(f"Could not process image edges: {str(e)}")

    def create_particle(self):
        x = random.randint(0, self.width - 1)
        y = random.randint(-50, 0)

        speed = random.uniform(self.particle_speed - 5, self.particle_speed + 5)

        wind_force = (self.wind_speed + random.uniform(-self.wind_randomness, self.wind_randomness)) * \
                     (1 if random.random() > 0.5 else -1)

        particle = RainParticle(
            x, y, speed, self.rain_color,
            wind_force=wind_force,
            drip_probability=self.drip_probability
        )

        return particle

    def update(self):
        particles_needed = self.max_particles - len(self.particles)
        if particles_needed > 0:
            batch_size = min(30, particles_needed)
            self.particles.extend([self.create_particle() for _ in range(batch_size)])

        self.particles = [p for p in self.particles if p.y < self.height and (not p.stuck or p.alpha > 0)]

        for particle in self.particles:
            particle.update(self.edges)

    def draw(self):
        self.screen.fill(self.bg_color)
        self.particle_surface.fill((0, 0, 0, 0))

        for particle in self.particles:
            particle.draw(self.particle_surface)

        self.screen.blit(self.particle_surface, (0, 0))
        pygame.display.flip()

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_r:
                        self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h),
                                                          pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)

            self.update()
            self.draw()
            pygame.display.set_caption(f'Rain Effect - FPS: {int(self.clock.get_fps())} (By AdnanZXG)')
            self.clock.tick(self.target_fps)

        pygame.quit()


class RainEffectApp:
    def __init__(self, root):
        self.root = root
        self.restart_app = False
        self.root.title("Rain Effect Configurator")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        window_width = min(500, int(screen_width * 0.6))
        window_height = min(600, int(screen_height * 0.7))

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.state('normal')

        self.root.configure(bg='#1E1E1E')

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_style()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.basic_frame = ttk.Frame(self.notebook)
        self.advanced_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.basic_frame, text='Basic')
        self.notebook.add(self.advanced_frame, text='Advanced')

        self.image_path = tk.StringVar()
        self.bg_color = tk.StringVar(value="#000000")
        self.rain_color = tk.StringVar(value="#FF0000")

        self.max_particles = tk.IntVar(value=7000)
        self.wind_speed = tk.DoubleVar(value=1.0)
        self.wind_randomness = tk.DoubleVar(value=0.5)
        self.drip_probability = tk.DoubleVar(value=0.4)
        self.particle_speed = tk.DoubleVar(value=15.0)

        self.create_basic_widgets()
        self.create_advanced_widgets()

    def configure_style(self):
        self.style.configure('TFrame', background='#1E1E1E')
        self.style.configure('TLabel',
                             foreground='white',
                             background='#1E1E1E',
                             font=('Arial', 10))
        self.style.configure('TButton',
                             background='#333333',
                             foreground='white',
                             font=('Arial', 10))
        self.style.configure('TNotebook',
                             background='#1E1E1E')
        self.style.map('TButton',
                       background=[('active', '#444444'), ('pressed', '#555555')])
        self.style.configure('TScale',
                             background='#1E1E1E',
                             troughcolor='#333333',
                             sliderthickness=10)

    def create_basic_widgets(self):
        image_label = ttk.Label(self.basic_frame, text="Select Image")
        image_label.pack(pady=(10, 5))

        image_frame = ttk.Frame(self.basic_frame)
        image_frame.pack(pady=5, padx=10, fill='x')

        image_entry = ttk.Entry(image_frame, textvariable=self.image_path, width=40)
        image_entry.pack(side=tk.LEFT, expand=True, fill='x', padx=(0, 5))

        browse_btn = ttk.Button(image_frame, text="Browse", command=self.browse_image)
        browse_btn.pack(side=tk.LEFT)

        color_frame = ttk.Frame(self.basic_frame)
        color_frame.pack(pady=10, padx=10, fill='x')

        bg_label = ttk.Label(color_frame, text="Background")
        bg_label.grid(row=0, column=0, padx=5)

        bg_entry = ttk.Entry(color_frame, textvariable=self.bg_color, width=10)
        bg_entry.grid(row=0, column=1, padx=5)

        bg_btn = ttk.Button(color_frame, text="Choose",
                            command=lambda: self.choose_color(self.bg_color, bg_entry))
        bg_btn.grid(row=0, column=2, padx=5)

        rain_label = ttk.Label(color_frame, text="Rain")
        rain_label.grid(row=1, column=0, padx=5, pady=5)

        rain_entry = ttk.Entry(color_frame, textvariable=self.rain_color, width=10)
        rain_entry.grid(row=1, column=1, padx=5, pady=5)

        rain_btn = ttk.Button(color_frame, text="Choose",
                              command=lambda: self.choose_color(self.rain_color, rain_entry))
        rain_btn.grid(row=1, column=2, padx=5, pady=5)

        start_btn = ttk.Button(self.basic_frame, text="Start Rain Effect", command=self.start_rain_effect)
        start_btn.pack(pady=20)

    def create_advanced_widgets(self):
        advanced_config = [
            ("Max Particles", self.max_particles, 1000, 10000, 0),
            ("Wind Speed", self.wind_speed, 0.0, 5.0, 2),
            ("Wind Randomness", self.wind_randomness, 0.0, 2.0, 2),
            ("Drip Probability", self.drip_probability, 0.0, 1.0, 2),
            ("Particle Speed", self.particle_speed, 5.0, 30.0, 1)
        ]

        for label_text, var, min_val, max_val, decimal_places in advanced_config:
            frame = ttk.Frame(self.advanced_frame)
            frame.pack(pady=10, padx=10, fill='x')

            label = ttk.Label(frame, text=label_text)
            label.pack(side=tk.LEFT)

            slider = ttk.Scale(frame,
                               from_=min_val,
                               to=max_val,
                               variable=var,
                               orient=tk.HORIZONTAL)
            slider.pack(side=tk.LEFT, expand=True, fill='x', padx=10)

            value_label = ttk.Label(frame, text='')
            value_label.pack(side=tk.LEFT)

            def create_update_func(label, var, decimal_places):
                def update_value(*args):
                    label.config(text=f"{var.get():.{decimal_places}f}")

                return update_value

            update_func = create_update_func(value_label, var, decimal_places)
            var.trace_add('write', update_func)

            update_func()

    def browse_image(self):
        filename = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if filename:
            self.image_path.set(filename)

    def choose_color(self, color_var, entry_widget):
        color = colorchooser.askcolor(title="Choose Color",
                                      color=color_var.get())
        if color[1]:
            color_var.set(color[1])
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, color[1])

    def start_rain_effect(self):
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

        if not self.image_path.get():
            messagebox.showerror("Error", "Please select an image")
            return

        try:
            current_config = {
                'image_path': self.image_path.get(),
                'bg_color': hex_to_rgb(self.bg_color.get()),
                'rain_color': hex_to_rgb(self.rain_color.get()),
                'max_particles': self.max_particles.get(),
                'wind_speed': self.wind_speed.get(),
                'wind_randomness': self.wind_randomness.get(),
                'drip_probability': self.drip_probability.get(),
                'particle_speed': self.particle_speed.get()
            }

            effect = RainEffect(**current_config)
            effect.run()

        except Exception as e:
            messagebox.showerror("Rain Effect Error",
                                 f"An error occurred while processing the image:\n\n{str(e)}\n\n"
                                 "Please choose a different image or check if the file is corrupted.")


def main():
    while True:
        root = tk.Tk()
        root.iconbitmap("icon.ico")
        app = RainEffectApp(root)
        root.mainloop()

        if not app.restart_app:
            break


if __name__ == '__main__':
    main()