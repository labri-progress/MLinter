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

echo "Exporting errors in database..."
python3 step_5_dependencies/export_errors_in_db.py "$execs_number" "$current_exec"
echo "Exporting errors in database... done"
