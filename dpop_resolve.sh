#!/bin/bash

output_root="results_dpop_3_taxis_3_taches"
mkdir -p "$output_root"  # Create main results directory

# Iterate over i (1 to 10)
for i in {1..10}; do
    instance_folder="$output_root/inst_$i"
    mkdir -p "$instance_folder"  # Create directory for each instance
    
    # Iterate over j (0, 5, 10, 15, 20, 25)
    for j in {0..25..5}; do
        yaml_file="fichiers_3_taxis_3_taches/inst_${i}_${j}.yaml"
        output_file="$instance_folder/result_${j}"
        
        # Run command in background (parallel execution)
        pydcop solve -a dpop "$yaml_file" > "$output_file" 2>&1 
    done
done

wait  # Wait for all background processes to finish

echo "All tasks completed!"