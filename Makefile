# -------------------------------------------
# Author: Urooj Asgher
# TU Dublin – PhD Researcher
# Energy Measurement Framework (Omegawatt)
# -------------------------------------------

PYTHON = python3

# Default target
all: appenergy

# Clean previous outputs
clean:
	@echo "Cleaning previous output files..."
	rm -f all_powerresults_omegawatt_varstd.txt \
	      Omegawatt-output.csv \
	      mxm_power.csv \
	      power_serial_mxm.txt \
	      power_parallel_mxm.txt
	@echo "Cleanup complete."

# Measure baseline power
baseline: clean
	$(PYTHON) run_basepower_omegawatt_var_std.py

# Run the serial MXM program only
run-mxm:
	chmod +x run_smxm.sh
	./run_smxm.sh

# Measure application energy (serial MXM)
appenergy: clean
	$(PYTHON) run_appenergy_smxm_omegawatt_stdvar.py


