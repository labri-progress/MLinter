#!/bin/bash

execs_number=1
current_exec=0
while getopts n:e: flag
do
    case "${flag}" in
        n) execs_number=${OPTARG};;
        e) current_exec=${OPTARG};;
        *) echo "Invalid option: ${flag}";;
    esac
done

echo "Extracting dataset for xp..."
python3 step_6_dependencies/extract_dataset_for_xp.py "$execs_number" "$current_exec"
echo "Extracting dataset... done"
