import pygame
import random
import math

class Task:
    def __init__(self, task_id, start, end):
        self.task_id = task_id
        self.start = start # Starting position of the task
        self.end = end # Ending position of the task
        self.cost = self.calculate_cost() # Euclidean distance between start and end

    def calculate_cost(self):
        return math.sqrt((self.start[0] - self.end[0]) ** 2 + (self.start[1] - self.end[1]) ** 2)

class Taxi:
    def __init__(self, taxi_id, position, color):
        self.taxi_id = taxi_id
        self.position = position
        self.color = color
        self.tasks = []
        self.total_cost = 0
        self.path = []  # Stores movement trail for visualization

    def add_task(self, task):
        if self.tasks:
            last_task_end = self.tasks[-1].end
            travel_cost = math.sqrt((last_task_end[0] - task.start[0]) ** 2 + (last_task_end[1] - task.start[1]) ** 2)
        else:
            travel_cost = math.sqrt((self.position[0] - task.start[0]) ** 2 + (self.position[1] - task.start[1]) ** 2)
        
        self.total_cost += travel_cost + task.cost
        self.tasks.append(task)

    def move_towards(self, target, speed=1):
        dx, dy = target[0] - self.position[0], target[1] - self.position[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > speed:
            dx, dy = dx / distance * speed, dy / distance * speed
        self.position = (self.position[0] + dx, self.position[1] + dy)
        self.path.append(self.position)  # Track movement

    def execute_tasks(self):
        if self.tasks:
            current_task = self.tasks[0]
            # Vérifier si le taxi est à la destination de la tâche
            if self.position == current_task.end:
                print(f"Taxi {self.taxi_id} a terminé la tâche {current_task.task_id}.")
                self.tasks.pop(0)  # Supprimer la tâche terminée
            elif self.position != current_task.start:
                print(f"Taxi {self.taxi_id} se déplace vers le départ de la tâche {current_task.task_id} ({current_task.start}).")
                self.move_towards(current_task.start)
            else:
                print(f"Taxi {self.taxi_id} exécute la tâche {current_task.task_id} et se dirige vers {current_task.end}.")
                self.move_towards(current_task.end)
        else:
            print(f"Taxi {self.taxi_id} est en attente sans tâche.")


class Environment:
    def __init__(self, size, num_taxis, task_frequency):
        self.size = size
        self.num_taxis = num_taxis
        self.task_frequency = task_frequency
        self.taxis = [
            Taxi(taxi_id=i, position=self.random_position(), color=self.random_color())
            for i in range(num_taxis)
        ]
        self.tasks = []
        self.time_step = 0

    def random_position(self):
        return (random.randint(0, self.size), random.randint(0, self.size))

    def random_color(self):
        return (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    def generate_tasks(self):
        num_new_tasks = random.randint(1, self.num_taxis)
        for i in range(num_new_tasks):
            start = self.random_position()
            end = self.random_position()
            task_id = f"Task_{self.time_step}_{i}"
            self.tasks.append(Task(task_id, start, end))

    def allocate_tasks(self):
        for task in self.tasks:
            best_taxi = None
            best_cost = float('inf')
            for taxi in self.taxis:
                if taxi.tasks:
                    last_task_end = taxi.tasks[-1].end
                else:
                    last_task_end = taxi.position

                travel_cost = math.sqrt((last_task_end[0] - task.start[0]) ** 2 + (last_task_end[1] - task.start[1]) ** 2)
                total_cost = travel_cost + task.cost
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_taxi = taxi

            if best_taxi:
                # print(f"Allocating {task.task_id}, start: {task.start}, end: {task.end} to Taxi {best_taxi.taxi_id}")
                best_taxi.add_task(task)
            else:
                print(f"Task {task.task_id} could not be allocated!")

        self.tasks = []  # Clear tasks after allocation


    # def step(self):
    #     self.time_step += 1
    #     if self.time_step % self.task_frequency == 0:
    #         self.generate_tasks()
    #     self.allocate_tasks()
    #     for taxi in self.taxis:
    #         taxi.execute_tasks()
    def step(self):
        self.time_step += 1
        print(f"\n=== Étape {self.time_step} ===")
        
        # Génération de nouvelles tâches
        if self.time_step % self.task_frequency == 0:
            self.generate_tasks()
            print(f"Tâches générées : {[task.task_id for task in self.tasks]}")

        # Allocation des tâches
        self.allocate_tasks()
        
        # Afficher l'état des taxis avant de bouger
        for taxi in self.taxis:
            print(f"Taxi {taxi.taxi_id}: Position {taxi.position}, "
                f"Tâches {[task.task_id for task in taxi.tasks]}")

        # Faire avancer les taxis
        for taxi in self.taxis:
            taxi.execute_tasks()


# Pygame Visualization
class Simulation:
    def __init__(self, environment, screen_size=600):
        pygame.init()
        self.env = environment
        self.screen_size = screen_size
        self.cell_size = screen_size // self.env.size
        self.screen = pygame.display.set_mode((screen_size, screen_size))
        pygame.display.set_caption("Taxi Fleet Simulation")
        self.clock = pygame.time.Clock()
        self.running = True
        self.delay = 500  # Delay in milliseconds between frames

    def draw_grid(self):
        for x in range(0, self.screen_size, self.cell_size):
            pygame.draw.line(self.screen, (200, 200, 200), (x, 0), (x, self.screen_size))
        for y in range(0, self.screen_size, self.cell_size):
            pygame.draw.line(self.screen, (200, 200, 200), (0, y), (self.screen_size, y))

    def draw_taxis(self):
        for taxi in self.env.taxis:
            # Draw path trail
            for i in range(len(taxi.path) - 1):
                start = (int(taxi.path[i][0] * self.cell_size), int(taxi.path[i][1] * self.cell_size))
                end = (int(taxi.path[i + 1][0] * self.cell_size), int(taxi.path[i + 1][1] * self.cell_size))
                pygame.draw.line(self.screen, taxi.color, start, end, 2)

            # Draw taxi
            x, y = int(taxi.position[0] * self.cell_size), int(taxi.position[1] * self.cell_size)
            pygame.draw.circle(self.screen, taxi.color, (x, y), self.cell_size // 3)

    def draw_tasks(self):
        for task in self.env.tasks:
            sx, sy = int(task.start[0] * self.cell_size), int(task.start[1] * self.cell_size)
            ex, ey = int(task.end[0] * self.cell_size), int(task.end[1] * self.cell_size)
            pygame.draw.circle(self.screen, (255, 0, 0), (sx, sy), self.cell_size // 4)
            pygame.draw.circle(self.screen, (0, 255, 0), (ex, ey), self.cell_size // 4)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.env.step()

            self.screen.fill((255, 255, 255))
            self.draw_grid()
            self.draw_tasks()
            self.draw_taxis()
            pygame.display.flip()

            pygame.time.delay(self.delay)  # Introduce delay to slow down the visualization

        pygame.quit()

# Configuration
#IMPORTANT: Each timestep, we generate m tasks, m>=n, n = number of taxis
environment_size = 20
num_taxis = 5
task_frequency = 5
env = Environment(size=environment_size, num_taxis=num_taxis, task_frequency=task_frequency)

# Run the simulation
sim = Simulation(env)
sim.run()
