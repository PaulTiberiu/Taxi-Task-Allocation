import random
import math
import pygame
import sys

# -------------------------------
# Classes principales
# -------------------------------
class Task:
    def __init__(self, start, end):
        self.start = start  # Position de départ (x, y)
        self.end = end      # Position d'arrivée (x, y)
        self.cost = self.calculate_distance(start, end)

    def calculate_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def __repr__(self):
        return f"Task(start={self.start}, end={self.end}, cost={self.cost:.2f})"


class Taxi:
    def __init__(self, taxi_id, position):
        self.taxi_id = taxi_id
        self.position = position  # Position actuelle (x, y)
        self.tasks = []           # Liste des tâches allouées
        self.total_cost = 0       # Coût total
        self.trajectory = []      # Liste des trajectoires pour visualisation
        self.current_task_index = 0  # Index de la tâche en cours
        self.finished_trajectory = []  # Trajectoires terminées pour affichage
        self.recent_trajectory = []  # Trajectoires terminées récemment
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Couleur aléatoire pour chaque taxi

    def calculate_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def assign_task(self, task):
        """Assigner une tâche au taxi et mettre à jour le coût."""
        self.tasks.append(task)
        # Ajouter la trajectoire vers la position de départ et la destination
        self.trajectory.append((self.position, task.start))
        self.trajectory.append((task.start, task.end))

    def execute_task(self):
        """Exécuter la tâche en cours et gérer les trajectoires."""
        if self.current_task_index < len(self.tasks):
            task = self.tasks[self.current_task_index]

            # Si le taxi doit d'abord se rendre au point de départ
            if self.position != task.start:
                self.recent_trajectory.append((self.position, task.start))
                self.position = task.start
                print(f"Taxi {self.taxi_id} moved to position {self.position}")
            else:
                # Aller à la destination
                self.recent_trajectory.append((self.position, task.end))
                self.position = task.end
                print(f"Taxi {self.taxi_id} moved to position {self.position}")

                # Passer à la tâche suivante
                self.current_task_index += 1
        
    def update_trajectories(self):
        """Mettre à jour les trajectoires pour les afficher un pas de temps supplémentaire."""
        self.finished_trajectory.extend(self.recent_trajectory)
        self.recent_trajectory = []  # Réinitialiser les nouvelles trajectoires

        
    def reset_finished_trajectory(self):
        """Réinitialiser la trajectoire terminée."""
        self.finished_trajectory = []

    def __repr__(self):
        return f"Taxi(id={self.taxi_id}, position={self.position}, total_cost={self.total_cost:.2f})"
    

# -------------------------------
# Environnement de simulation
# -------------------------------
class Environment:
    def __init__(self, grid_size, num_taxis, task_frequency, num_iterations, delay=200):
        self.grid_size = grid_size
        self.num_taxis = num_taxis
        self.task_frequency = task_frequency  # Fréquence d'arrivée des tâches (T)
        self.num_iterations = num_iterations  # Nombre total d'itérations
        self.taxis = [Taxi(taxi_id=i, position=self.random_position()) for i in range(num_taxis)]
        self.tasks = []  # Liste des tâches en attente
        self.time = 0    # Temps actuel
        self.delay = delay  # Délai en millisecondes pour ralentir l'exécution (nous n'en aurons plus besoin ici)

    def random_position(self):
        """Générer une position aléatoire dans la grille."""
        return (random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1))

    def generate_tasks(self):
        """Générer des tâches aléatoires."""
        num_tasks = random.randint(1, self.num_taxis)  # Par exemple, jusqu'à 1 tâche par taxi
        new_tasks = [Task(start=self.random_position(), end=self.random_position()) for _ in range(num_tasks)]
        self.tasks.extend(new_tasks)
        print(f"\n[Time {self.time}] Generated {len(new_tasks)} new tasks: {new_tasks}")

    def allocate_tasks(self):
        """Allouer les tâches aux taxis en minimisant les coûts."""
        for task in self.tasks:
            print(f"\n[Time {self.time}] Allocating task {task}")
            
            best_taxi = None
            best_cost = float('inf')

            # Trouver le taxi le plus proche du début de la tâche
            for taxi in self.taxis:
                cost = taxi.calculate_distance(taxi.position, task.start)
                print(f"Taxi {taxi.taxi_id} has cost {cost:.2f} for task {task}")

                if cost < best_cost:
                    best_cost = cost
                    best_taxi = taxi
            
            # Allouer la tâche au taxi sélectionné
            best_taxi.assign_task(task)
            print(f"Assigned task {task} to Taxi {best_taxi.taxi_id} with cost {best_cost:.2f}")
        
        # Vider la liste des tâches après allocation
        self.tasks = []


# -------------------------------
# Visualisation avec Pygame
# -------------------------------
def visualize_with_pygame(env):
    pygame.init()
    
    # Configuration de l'affichage
    SCREEN_SIZE = 600
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("Taxi Task Allocation Simulation")
    clock = pygame.time.Clock()

    cell_size = SCREEN_SIZE // env.grid_size

    def draw_line(screen, start, end, color):
        pygame.draw.line(
            screen, color,
            (start[1] * cell_size + cell_size // 2, start[0] * cell_size + cell_size // 2),  # Colonne -> x, Ligne -> y
            (end[1] * cell_size + cell_size // 2, end[0] * cell_size + cell_size // 2),      # Colonne -> x, Ligne -> y
            3
        )


    def draw_grid(screen):
        """Dessiner la grille avec les indices des cases sur les bords."""
        font = pygame.font.SysFont("Arial", 12)
        
        for x in range(env.grid_size):
            for y in range(env.grid_size):
                # Dessiner les lignes de la grille
                pygame.draw.line(screen, (0, 0, 0), (x * cell_size, 0), (x * cell_size, SCREEN_SIZE))
                pygame.draw.line(screen, (0, 0, 0), (0, y * cell_size), (SCREEN_SIZE, y * cell_size))
        
        # Numéros sur le bord supérieur et inférieur (axe X)
        for x in range(env.grid_size):
            text = font.render(f"{x}", True, (0, 0, 0))
            screen.blit(text, (x * cell_size + cell_size // 2 - text.get_width() // 2, 0))
            screen.blit(text, (x * cell_size + cell_size // 2 - text.get_width() // 2, SCREEN_SIZE - text.get_height()))
        
        # Numéros sur le bord gauche et droit (axe Y)
        for y in range(env.grid_size):
            text = font.render(f"{y}", True, (0, 0, 0))
            screen.blit(text, (0, y * cell_size + cell_size // 2 - text.get_height() // 2))
            screen.blit(text, (SCREEN_SIZE - text.get_width(), y * cell_size + cell_size // 2 - text.get_height() // 2))

    running = True
    time_step = 0
    while running and time_step < env.num_iterations:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # Si la touche "Entrée" est pressée, avancer le temps
                if event.key == pygame.K_RETURN:
                    # Générer des tâches si nécessaire
                    if time_step % env.task_frequency == 0:
                        env.generate_tasks()
                    if env.tasks:
                        env.allocate_tasks()

                    # Dessiner l'environnement
                    screen.fill((255, 255, 255))
                    draw_grid(screen)  # Dessiner la grille avec les indices des cases
                    
                    for taxi in env.taxis:
                        # # Dessiner la trajectoire finie
                        # for line in taxi.finished_trajectory:
                        #     draw_line(screen, line[0], line[1], taxi.color)

                        # # Dessiner la position actuelle
                        # # pygame.draw.circle(screen, taxi.color, 
                        # #                    (taxi.position[0] * cell_size + cell_size // 2, taxi.position[1] * cell_size + cell_size // 2), 10)
                        # pygame.draw.circle(
                        #     screen, taxi.color,
                        #     (taxi.position[1] * cell_size + cell_size // 2,  # Colonne -> axe x
                        #     taxi.position[0] * cell_size + cell_size // 2), # Ligne -> axe y
                        #     10
                        # )

                        
                        # # Afficher le numéro du taxi au-dessus de sa position
                        # font = pygame.font.SysFont("Arial", 14)
                        # text = font.render(f"Taxi {taxi.taxi_id}", True, (0, 0, 0))
                        # screen.blit(
                        #     text,
                        #     (taxi.position[1] * cell_size + cell_size // 2 - text.get_width() // 2,  # Colonne -> axe x
                        #     taxi.position[0] * cell_size + cell_size // 2 - 20)  # Ligne -> axe y
                        # )


                        # # Exécuter la tâche
                        # taxi.execute_task()

                        # Mettre à jour les trajectoires avant de dessiner
                        taxi.update_trajectories()

                        # Dessiner les trajectoires finies
                        for line in taxi.finished_trajectory:
                            draw_line(screen, line[0], line[1], taxi.color)

                        # Dessiner les trajectoires récentes
                        for line in taxi.recent_trajectory:
                            draw_line(screen, line[0], line[1], (0, 0, 0))  # Couleur noire pour différencier

                        # Dessiner la position actuelle
                        pygame.draw.circle(
                            screen, taxi.color,
                            (taxi.position[1] * cell_size + cell_size // 2,
                            taxi.position[0] * cell_size + cell_size // 2),
                            10
                        )
                        
                        # Afficher le numéro du taxi
                        font = pygame.font.SysFont("Arial", 14)
                        text = font.render(f"Taxi {taxi.taxi_id}", True, (0, 0, 0))
                        screen.blit(
                            text,
                            (taxi.position[1] * cell_size + cell_size // 2 - text.get_width() // 2,
                            taxi.position[0] * cell_size + cell_size // 2 - 20)
                        )

                        # Exécuter la tâche
                        taxi.execute_task()

                        # Supprimer les lignes terminées après affichage
                        if not taxi.tasks or taxi.current_task_index >= len(taxi.tasks):
                            taxi.reset_finished_trajectory()

                    pygame.display.flip()
                    
                    # Incrémenter le pas de temps et afficher l'heure
                    env.time += 1
                    print(f"Time {env.time}")

                    # Incrémenter le pas de temps
                    time_step += 1

    pygame.quit()
    sys.exit()

# -------------------------------
# Main Program
# -------------------------------
if __name__ == "__main__":
    GRID_SIZE = 20
    NUM_TAXIS = 3
    TASK_FREQUENCY = 5
    NUM_ITERATIONS = 30
    DELAY = 500  # Délai de 500 millisecondes (0.5 seconde) entre chaque itération

    env = Environment(grid_size=GRID_SIZE, num_taxis=NUM_TAXIS, task_frequency=TASK_FREQUENCY, num_iterations=NUM_ITERATIONS, delay=DELAY)
    visualize_with_pygame(env)
