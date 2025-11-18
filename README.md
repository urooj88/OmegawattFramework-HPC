# **Energy Measurement Framework for Data-Parallel Matrix Multiplication (MXM)**

This repository contains the code and scripts used to measure the energy consumption of a serial matrix-multiplication (MXM) workload using the Omegawatt power-measurement tool.
The framework is designed so that users can run the full experiment without manually compiling or editing any files. All compilation steps are handled automatically inside the scripts.


## **Repository Structure**

├── smxm.c                               # Serial matrix multiplication code
├── esmxm                                # Compiled executable (optional)
├── run_smxm.sh                          # Script to compile and run MXM
├── run_basepower_omegawatt_var_std.py   # Script to measure baseline power
├── run_appenergy_smxm_omegawatt_stdvar.py  # Script to measure application energy
├── power_serial_mxm.txt                 # Raw power log (optional)
├── Omegawatt-output.csv                 # Baseline power results
├── mxm_power.csv                        # Application power data
├── all_powerresults_omegawatt_varstd.txt # Summary of energy results
├── README.md                            # Documentation

## **Requirements**

Before running the scripts, ensure your system has:

* Python 3
* Omegawatt power meter or access to its serial device
* Bash shell (Linux / macOS)
* GCC (used automatically inside the scripts)

No manual compilation is required — the shell scripts take care of it.


## **How to Run the Framework**

The project provides two main measurement modes.


### **1. Measure Baseline System Power (Idle)**

To record the idle/baseline power of the system:

```bash
python3 run_basepower_omegawatt_var_std.py
```

This script:

* Starts Omegawatt
* Collects baseline power readings
* Computes variance and standard deviation
* Saves results into:


Omegawatt-output.csv


### **2. Measure Energy Consumption of the MXM Application**

To measure the energy consumption of the serial matrix multiplication program:

```bash
python3 run_appenergy_smxm_omegawatt_stdvar.py
```

This script automatically:

* Calls `run_smxm.sh`
* Compiles and runs `smxm.c`
* Monitors energy using Omegawatt
* Saves results into:

```
mxm_power.csv
all_powerresults_omegawatt_varstd.txt
power_serial_mxm.txt
```

Again, no file compilation or editing is required.


## **Makefile Support**

The repository also includes a simple Makefile so users can run the main steps with short commands:

```bash
make baseline      # Measure idle/baseline power
make appenergy     # Measure MXM application energy
make run-mxm       # Only run the serial MXM program
```

## **How a User Runs Everything**

After cloning the repository:

```bash
git clone https://github.com/yourusername/hpc-energy-measurement-framework.git
cd hpc-energy-measurement-framework
```

Then simply choose:

* **Baseline Only:**
  `make baseline`

* **Application Energy:**
  `make appenergy`

* **Run the Program Only:**
  `make run-mxm`

No manual setup, compilation, or configuration is needed.



