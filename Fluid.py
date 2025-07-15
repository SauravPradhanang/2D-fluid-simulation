import pygame
import numpy as np

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Fluid Simulation")

# Particle settings
particles = []
max_particles = 100
particle_limit_min = 10
particle_limit_max = 300
radius = 5
gravity = np.array([0, 0.1])

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Slider setup
slider_width = 300
slider_height = 10
slider_x = (width - slider_width) // 2
slider_y = height - 30
slider_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)

handle_width = 20
handle_height = 30
handle_x = slider_x + int(slider_width * (max_particles - particle_limit_min) / (particle_limit_max - particle_limit_min)) - handle_width // 2
handle_y = slider_y - 10  
handle_rect = pygame.Rect(handle_x, handle_y, handle_width, handle_height)

# circle following mouse 
circle_radius_min = 10
circle_radius_max = 150
circle_radius = 50

circle_slider_width = 300
circle_slider_height = 10
circle_slider_x = (width - circle_slider_width)// 2
circle_slider_y = height - 90
circle_slider_rect = pygame.Rect(circle_slider_x,circle_slider_y,circle_slider_width,circle_slider_height)

circle_handler_width = 20
circle_handler_height = 30
circle_handler_x = circle_slider_x + int(circle_slider_width * (circle_radius - circle_radius_min) / (circle_radius_max - circle_radius_min))- circle_handler_width//2
circle_handler_y = circle_slider_y - 10 
circle_handler_rect = pygame.Rect(circle_handler_x,circle_handler_y,circle_handler_width,circle_handler_height)

circle_dragging = False

# Smoothing radius parameters
smoothing_radius_min = 20
smoothing_radius_max = 150
smoothing_radius = 50

# Smoothing radius slider geometry
smoothing_slider_width = 300
smoothing_slider_height = 10
smoothing_slider_x = (width - smoothing_slider_width) // 2
smoothing_slider_y = height - 140  # place at the bottom
smoothing_slider_rect = pygame.Rect(smoothing_slider_x, smoothing_slider_y, smoothing_slider_width, smoothing_slider_height)

smoothing_handle_width = 20
smoothing_handle_height = 30
smoothing_handle_x = smoothing_slider_x + int(smoothing_slider_width * (smoothing_radius - smoothing_radius_min) / (smoothing_radius_max - smoothing_radius_min)) - smoothing_handle_width // 2
smoothing_handle_y = smoothing_slider_y - 10
smoothing_handle_rect = pygame.Rect(smoothing_handle_x, smoothing_handle_y, smoothing_handle_width, smoothing_handle_height)

smoothing_dragging = False

dragging = False 

# Function to spawn particles
def spawn_particles(n):
    for _ in range(n):
        pos = np.random.rand(2) * np.array([width, height])
        vel = (np.random.rand(2) - 0.5) * 10
        particles.append({
            'pos': pos,
            'vel': vel,
            'smoothing_radius': smoothing_radius
        })

# Spawn initial particles
spawn_particles(max_particles) 

# Smoothing kernel
def SmoothingKernel(radius, dst):
    if dst > radius:
        return 0
    return 1 - dst / radius

def calculate_density(sample_point, positions, smoothing_radius):
    density = 0.0
    mass = 1.0

    for position in positions:
        dst = np.linalg.norm(position - sample_point)
        if dst < smoothing_radius:
            influence = SmoothingKernel(smoothing_radius, dst)
            density += mass * influence

    return density

# Particle physics update
def update_particles():
    for p in particles:
        p['vel'] += gravity
        p['pos'] += p['vel']

        if p['pos'][0] <= 0 or p['pos'][0] >= width:
            p['vel'][0] *= -1
        if p['pos'][1] <= 0:
            p['vel'][1] *= -0.8
            p['pos'][1] = 0
        elif p['pos'][1] >= height:
            p['vel'][1] *= -0.8
            p['pos'][1] = height

    # Particle-particle collisions
    for i in range(len(particles)):
        for j in range(i + 1, len(particles)):
            p1 = particles[i]
            p2 = particles[j]
            pos1 = p1['pos']
            pos2 = p2['pos']
            dist = np.linalg.norm(pos1 - pos2)

            if dist < 2 * radius and dist != 0:
                normal = (pos2 - pos1) / dist
                tangent = np.array([-normal[1], normal[0]])

                v1n = np.dot(p1['vel'], normal)
                v1t = np.dot(p1['vel'], tangent)
                v2n = np.dot(p2['vel'], normal)
                v2t = np.dot(p2['vel'], tangent)

                v1n, v2n = v2n, v1n

                p1['vel'] = v1n * normal + v1t * tangent
                p2['vel'] = v2n * normal + v2t * tangent

                overlap = 2 * radius - dist
                correction = normal * (overlap / 2)
                p1['pos'] -= correction
                p2['pos'] += correction

# Main loop
running = True
while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if handle_rect.collidepoint(event.pos):
                dragging = True
            if circle_handler_rect.collidepoint(event.pos):
                circle_dragging = True
            if smoothing_handle_rect.collidepoint(event.pos):
                smoothing_dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
            circle_dragging = False
            smoothing_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                mouse_x = event.pos[0]
                handle_rect.x = max(slider_x, min(mouse_x - handle_width // 2, slider_x + slider_width - handle_width))

                relative_pos = (handle_rect.x + handle_width // 2 - slider_x) / slider_width
                target_particles = int(particle_limit_min + relative_pos * (particle_limit_max - particle_limit_min))

                if target_particles > len(particles):
                    spawn_particles(target_particles - len(particles))
                elif target_particles < len(particles):
                    del particles[target_particles:]
            if circle_dragging:
                mouse_x = event.pos[0]
                circle_handler_rect.x = max(circle_slider_x, min(mouse_x - circle_handler_width // 2, circle_slider_x + circle_slider_width - circle_handler_width))
                relative_pos = (circle_handler_rect.x + circle_handler_width // 2 - circle_slider_x) / circle_slider_width
                circle_radius = int(circle_radius_min + relative_pos * (circle_radius_max - circle_radius_min))
            if smoothing_dragging:
                mouse_x = event.pos[0]
                smoothing_handle_rect.x = max(smoothing_slider_x, min(mouse_x - smoothing_handle_width // 2, smoothing_slider_x + smoothing_slider_width - smoothing_handle_width))
                relative_pos = (smoothing_handle_rect.x + smoothing_handle_width // 2 - smoothing_slider_x) / smoothing_slider_width
                smoothing_radius = int(smoothing_radius_min + relative_pos * (smoothing_radius_max - smoothing_radius_min))


    update_particles()

    screen.fill(BLACK)

    # Draw smoothing radius slider
    pygame.draw.rect(screen, GRAY, smoothing_slider_rect)
    pygame.draw.rect(screen, WHITE, smoothing_handle_rect)

    # Display current smoothing radius
    smoothing_text = font.render(f"Smoothing Radius: {smoothing_radius}", True, WHITE)
    screen.blit(smoothing_text, (smoothing_slider_x, smoothing_slider_y - 30))

    # Draw the circle following the mouse
    mouse_pos = pygame.mouse.get_pos()
    pygame.draw.circle(screen, (0, 255, 0), mouse_pos, circle_radius, 1)

    mouse_pos_np = np.array(mouse_pos, dtype=float)
    density_inside_circle = calculate_density(mouse_pos_np, [p['pos'] for p in particles], smoothing_radius)

    # Render the density value as text
    density_text = font.render(f"Density: {density_inside_circle:.2f}", True, WHITE)
    screen.blit(density_text, (mouse_pos[0] + circle_radius + 10, mouse_pos[1] - 10))

    # Draw the circle radius slider
    pygame.draw.rect(screen, GRAY, circle_slider_rect)
    pygame.draw.rect(screen, WHITE, circle_handler_rect)

    # Display circle radius value
    circle_text = font.render(f"Circle Radius: {circle_radius}", True, WHITE)
    screen.blit(circle_text, (circle_slider_x, circle_slider_y - 30))

    # Draw particles with blue gradient shading first, then white center dot
    for p in particles:
        # Update smoothing_radius for all particles from slider value
        p['smoothing_radius'] = smoothing_radius

        # Draw blue gradient shading based on smoothing kernel
        smoothing_surface = pygame.Surface((smoothing_radius * 2, smoothing_radius * 2), pygame.SRCALPHA)
        center = smoothing_radius

        for r in range(smoothing_radius, radius, -1):  # from smoothing_radius down to radius+1 to avoid overlap
            alpha = int(255 * SmoothingKernel(smoothing_radius, r))
            if alpha > 0:
                color = (0, 0, 255, alpha)
                pygame.draw.circle(smoothing_surface, color, (center, center), r)

        screen.blit(smoothing_surface, (p['pos'][0] - smoothing_radius, p['pos'][1] - smoothing_radius))

        # Draw white particle dot at center ON TOP
        pygame.draw.circle(screen, WHITE, p['pos'].astype(int), radius)

    # Draw slider
    pygame.draw.rect(screen, GRAY, slider_rect)
    pygame.draw.rect(screen, WHITE, handle_rect)

    # Display particle count
    text = font.render(f"Particles: {len(particles)}", True, WHITE)
    screen.blit(text, (slider_x, slider_y - 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
