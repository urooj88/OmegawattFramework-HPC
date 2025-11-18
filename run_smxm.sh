#!/bin/bash

# Check if the C source code file exists
if [ ! -f smxm.c ]; then
    echo "Error: smxm.c not found!"
    exit 1
fi

# Compile the C source code
echo "Compiling smxm.c..."
gcc -o esmxm smxm.c

# Check if the compilation was successful
if [ $? -eq 0 ]; then
    echo "Compilation successful."
else
    echo "Compilation failed."
    exit 1
fi

# Define a fixed problem size inside the script
problemSize=2024

# Run the compiled executable with the fixed problem size
echo "Running the matrix multiplication program with problem size $problemSize..."
./esmxm $problemSize
### if you want change size set inside this 
