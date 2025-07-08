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
gravity = np.array([0, 0.2])
collison_damping = 0.8

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Function to spawn all particles at the start
def spawn_particles(n):
    spacing = 40  # spacing between particles to avoid overlap
    grid_cols = int(np.sqrt(n))
    grid_rows = int(np.ceil(n / grid_cols))

    grid_width = grid_cols * spacing
    grid_height = grid_rows * spacing

    start_x = width // 2 - grid_width // 2
    start_y = height // 2 - grid_height // 2

    count = 0
    for i in range(grid_cols):
        for j in range(grid_rows):
            if count >= n:
                return
            pos = np.array([
                start_x + i * spacing + spacing // 2,
                start_y + j * spacing + spacing // 2
            ], dtype=float)
            vel = (np.random.rand(2) - 0.5) * 4  # small random velocity
            particles.append({
                'pos': pos,
                'vel': vel
            })
            count += 1

#Smoothing Kernel
def SmoothingKernel(smoothingRadius, distance):
    volume = (np.pi)*(smoothingRadius**8)/4
    value = max(0, (smoothingRadius**2)-(distance**2))
    return (value**3)/volume
    
# Slider setup
slider_width = 300
slider_height = 10
slider_x = (width - slider_width) // 2
slider_y = height - 50
slider_rect = pygame.Rect(slider_x, slider_y, slider_width, slider_height)

handle_width = 20
handle_height = 30
handle_x = slider_x + int(slider_width * (max_particles - particle_limit_min) / (particle_limit_max - particle_limit_min)) - handle_width // 2
handle_y = slider_y - 10  # ✅ corrected
handle_rect = pygame.Rect(handle_x, handle_y, handle_width, handle_height)

dragging = False  # ✅ corrected

# Function to spawn particles
# def spawn_particles(n):
#     for _ in range(n):
#         pos = np.random.rand(2) * np.array([width, height])
#         vel = (np.random.rand(2) - 0.5) * 10
#         particles.append({
#             'pos': pos,
#             'vel': vel
#         })

# Spawn initial particles
spawn_particles(max_particles)  # ✅ corrected

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

                # Swap normal components for elastic collision
                v1n, v2n = v2n*collison_damping, v1n*collison_damping

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

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

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

    update_particles()

    screen.fill(BLACK)

    for p in particles:
        pygame.draw.circle(screen, RED, p['pos'].astype(int), radius)

    # Draw slider
    pygame.draw.rect(screen, GRAY, slider_rect)
    pygame.draw.rect(screen, WHITE, handle_rect)

    # Display particle count
    text = font.render(f"Particles: {len(particles)}", True, WHITE)
    screen.blit(text, (slider_x, slider_y - 30))

    # Draw slider
    pygame.draw.rect(screen, GRAY, slider_rect)
    pygame.draw.rect(screen, WHITE, handle_rect)

    # Display particle count
    text = font.render(f"Particles: {len(particles)}", True, WHITE)
    screen.blit(text, (slider_x, slider_y - 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
