from partie1_cocoma import *

def generate_file_yaml(env,nom_fic):
    list_taxis_env=env.taxis
    list_taches_env=env.tasks
    list_taxi=[]
    list_taches=[]
    for i in range(1,len(list_taxis_env)+1):
        list_taxi.append(f"t_{i}")
    
    for i in range(1,len(list_taches_env)+1):
        list_taches.append(f"j_{i}")
        
    with open(nom_fic,"w") as f:
        f.write("name: Allocation Problem \n")
        f.write("objective: min \n")
        f.write("\n")

        #Ecriture des domaines dans le fichier yaml
        f.write("domains: \n")
        f.write("   taches: \n" )
        f.write("      values: ")
        f.write("[")
        for i in range(len(list_taches)):
            f.write(list_taches[i])
            if i<len(list_taches)-1:
                f.write(",")
        f.write("]")
        f.write("\n")

        #Ecriture des variables dans le fichier yaml
        f.write("variables: \n")
        for taxi in list_taxi:
            f.write("   ")
            f.write(taxi)
            f.write(" : \n")
            f.write("      domain: taches \n")
        f.write("\n")

        f.write("constaraints: \n")
        for i in range(len(list_taxi)):
            f.write(f"   pref_{i+1}: \n")
            f.write("      type: extensional \n")
            f.write(f"      variables: {list_taxi[i]} \n")
            f.write("      values: \n")
            for j in range(len(list_taches)):
                f.write(f"         {j+1}: {list_taches[j]} \n")
            f.write("\n")
        
        for i in range(len(list_taxi)):
            for j in range(len(list_taxi)):
                if i<j:
                    f.write(f"   dist_{list_taxi[i]}_{list_taxi[j]}: \n")
                    f.write("      type: intention \n")
                    f.write(f"      function: 100 if {list_taxi[i]}=={list_taxi[j]} else 0 \n")
                    f.write("\n")
        
        for i in range(len(list_taxi)):
            for j in range(len(list_taches)):
                f.write(f"   dist_{list_taxi[i]}_{list_taches[j]}: \n")
                f.write("      type: intention \n")
                f.write(f"      function: {list_taches_env[j].cost+list_taxis_env[i].calculate_distance(list_taxis_env[i].position,list_taches_env[j].start)} if {list_taxi[i]}=={j+1} else 0 \n")
                f.write("\n")

        
        f.write("\n")
        f.write(f"agents: ")
        f.write("[")
        for i in range(len(list_taxi)):
            f.write(list_taxi[i])
            if i<len(list_taxi)-1:
                f.write(",")
        f.write("]")


GRID_SIZE = 20
NUM_TAXIS = 3
TASK_FREQUENCY = 5
NUM_ITERATIONS = 30
DELAY = 500  # Délai de 500 millisecondes (0.5 seconde) entre chaque itération

env=Environment(grid_size=GRID_SIZE, num_taxis=NUM_TAXIS, task_frequency=TASK_FREQUENCY, num_iterations=NUM_ITERATIONS, delay=DELAY)
env.generate_tasks()
generate_file_yaml(env,"iter1.yaml")