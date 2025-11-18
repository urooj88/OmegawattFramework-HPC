
# Author: Urooj Asgher
# Affiliation: Technological University Dublin (TU Dublin)
# Role: PhD Student [HPC-Nexus Lab]
# Email: uroojasgher@gmail.com
#---------------------------------------------

#!/usr/bin/env python3

import subprocess
import time
import pandas as pd
import os
import argparse
from pathlib import Path
import signal
import sys
from datetime import datetime, timedelta
import json

def measure_baseline():
    """Measure baseline power using existing script"""
    print("\nMeasuring Baseline Power Consumption...")
    print("=======================================")
    
    cmd = [
        'python3', 'run_basepower_omegawatt_var_std.py',
        '--repetitions', '20',
        '--measurement-time', '10',
        '--sleep', '2'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        # Read the baseline power from the correct file name
        with open("all_powerresults_omegawatt_varstd.txt", 'r') as f:
            baseline_data = f.read()
            for line in baseline_data.split('\n'):
                if "Average Power Consumption" in line:
                    baseline_power = float(line.split()[8])  # Adjusted index to match new format
                    break
        print(f"Baseline power measured: {baseline_power:.2f} W")
        return baseline_power
    except Exception as e:
        print(f"Error measuring baseline: {e}")
        return None

def run_application(app_type, matrix_size, num_threads=None):
    """Run the matrix multiplication application"""
    if app_type == 'serial':
        cmd = ["./run_smxm.sh"]
    else:  # parallel
        cmd = ["./run_pmxm.sh"]
        if num_threads:
            os.environ['OMP_NUM_THREADS'] = str(num_threads)
    
    try:
        start_time = time.time()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        end_time = time.time()
        execution_time = end_time - start_time
        
        if process.returncode != 0:
            print(f"Error running application: {stderr.decode()}")
            return None, 0
        
        return stdout.decode(), execution_time
    except Exception as e:
        print(f"Error running application: {e}")
        return None, 0

def process_power_data(csv_file):
    """Process power measurements from CSV file"""
    try:
        df = pd.read_csv(csv_file)
        power1 = df['#activepow1']
        power5 = df['#activepow5']
        total_power = power1 + power5
        
        stats = {
            'mean': total_power.mean(),
            'min': total_power.min(),
            'max': total_power.max(),
            'std': total_power.std(),
            'var': total_power.var(),
            'power1_mean': power1.mean(),
            'power1_std': power1.std(),
            'power1_var': power1.var(),
            'power5_mean': power5.mean(),
            'power5_std': power5.std(),
            'power5_var': power5.var()
        }
        
        print(f"Plug 1 measurements:")
        print(f"  Average power: {stats['power1_mean']:.2f} W")
        print(f"  Standard deviation: {stats['power1_std']:.2f} W")
        print(f"  Variance: {stats['power1_var']:.2f} W²")
        
        print(f"\nPlug 5 measurements:")
        print(f"  Average power: {stats['power5_mean']:.2f} W")
        print(f"  Standard deviation: {stats['power5_std']:.2f} W")
        print(f"  Variance: {stats['power5_var']:.2f} W²")
        
        print(f"\nTotal measurements:")
        print(f"  Total average power: {stats['mean']:.2f} W")
        print(f"  Total standard deviation: {stats['std']:.2f} W")
        print(f"  Total variance: {stats['var']:.2f} W²")
        
        return stats
    except Exception as e:
        print(f"Error processing CSV data: {e}")
        return None

def measure_app_power(app_type, matrix_size, num_threads=None):
    """Measure power while running the application"""
    output_dir = "."
    results_file = os.path.join(output_dir, f"power_{app_type}_mxm.txt")
    
    # Remove old results file if it exists
    if os.path.exists(results_file):
        os.remove(results_file)
    
    # First get baseline power
    baseline_power = measure_baseline()
    if baseline_power is None:
        return
    
    print("\nMeasuring Application Power...")
    print("=============================")
    
    # Start continuous power monitoring
    monitor_process = subprocess.Popen([
        "/home/uasgher/wattmeter-readinstall/wattmetre-read/v3/wattmetre-readnew2",
        "--tty=/dev/ttyUSB0", "--nb=6"
    ], stdout=open("mxm_power.csv", "w"))
    
    time.sleep(1)  # Wait for monitoring to start
    
    # Run the application
    print(f"\nRunning {app_type} matrix multiplication...")
    output, execution_time = run_application(app_type, matrix_size, num_threads)
    if output is None:
        monitor_process.terminate()
        return
    
    time.sleep(1)  # Wait for final measurements
    
    # Stop monitoring
    monitor_process.terminate()
    try:
        monitor_process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        monitor_process.kill()
        monitor_process.wait()
    
    # Process the power data
    execution_stats = process_power_data("mxm_power.csv")
    if execution_stats is None:
        print("Failed to process power data")
        return
    
    # Calculate power and energy
    execution_power = execution_stats['mean']
    power_increase = execution_power - baseline_power
    
    # Calculate energies
    baseline_energy_joules = baseline_power * execution_time
    total_energy_joules = execution_power * execution_time
    dynamic_energy_joules = power_increase * execution_time
    
    # Convert to Watt-hours
    baseline_energy_wh = baseline_energy_joules / 3600
    total_energy_wh = total_energy_joules / 3600
    dynamic_energy_wh = dynamic_energy_joules / 3600
    
    # Save results
    with open(results_file, 'w') as f:
        f.write(f"MATRIX MULTIPLICATION ENERGY REPORT ({app_type})\n")
        f.write("=========================================\n\n")
        
        f.write("1. Baseline Measurements\n")
        f.write("----------------------\n")
        f.write(f"Baseline Power: {baseline_power:.2f} W\n\n")
        
        f.write("2. Application Measurements\n")
        f.write("-------------------------\n")
        f.write(f"Total Power during execution: {execution_power:.2f} W\n")
        f.write(f"Dynamic Power (increase): {power_increase:.2f} W\n")
        f.write(f"Peak Power: {execution_stats['max']:.2f} W\n")
        f.write(f"Standard Deviation: {execution_stats['std']:.2f} W\n")
        f.write(f"Variance: {execution_stats['var']:.2f} W²\n")
        f.write(f"Execution Time: {execution_time:.3f} seconds\n\n")
        
        f.write("3. Energy Analysis\n")
        f.write("----------------\n")
        f.write(f"Baseline Energy: {baseline_energy_wh:.6f} Wh ({baseline_energy_joules:.2f} J)\n")
        f.write(f"Total Energy: {total_energy_wh:.6f} Wh ({total_energy_joules:.2f} J)\n")
        f.write(f"Dynamic Energy: {dynamic_energy_wh:.6f} Wh ({dynamic_energy_joules:.2f} J)\n\n")
        
        f.write("4. Application Details\n")
        f.write("--------------------\n")
        f.write(f"Application Type: {app_type}\n")
        if num_threads:
            f.write(f"Number of Threads: {num_threads}\n")
    
    print(f"\nResults have been saved to: {results_file}")
    
    # Print summary
    print("\nENERGY CONSUMPTION SUMMARY:")
    print("==========================")
    print(f"\n1. Baseline Measurements:")
    print(f"   Average Power: {baseline_power:.2f} W")
    
    print(f"\n2. During Application Run:")
    print(f"   Execution Time: {execution_time:.3f} seconds")
    print(f"   Total Power: {execution_power:.2f} W")
    print(f"   Dynamic Power (increase): {power_increase:.2f} W")
    print(f"   Standard Deviation: {execution_stats['std']:.2f} W")
    print(f"   Variance: {execution_stats['var']:.2f} W²")
    
    print(f"\n3. Energy Breakdown:")
    print(f"   Baseline Energy: {baseline_energy_wh:.6f} Wh ({baseline_energy_joules:.2f} J)")
    print(f"   Total Energy: {total_energy_wh:.6f} Wh ({total_energy_joules:.2f} J)")
    print(f"   Dynamic Energy: {dynamic_energy_wh:.6f} Wh ({dynamic_energy_joules:.2f} J)")

def cleanup_previous_outputs():
    """Remove all previous output files before starting new measurements"""
    files_to_remove = [
        "all_powerresults_omegawatt_varstd.txt",
        "Omegawatt-output.csv",
        "mxm_power.csv",
        "power_serial_mxm.txt",
        "power_parallel_mxm.txt"
    ]
    
    print("Cleaning up previous output files...")
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"  Removed: {file}")
            except Exception as e:
                print(f"  Error removing {file}: {e}")
    print("Cleanup complete.\n")

def main():
    parser = argparse.ArgumentParser(description='Measure application energy consumption')
    parser.add_argument('--app-type', choices=['serial', 'parallel'], default='serial',
                      help='Type of application to run (default: serial)')
    parser.add_argument('--threads', type=int,
                      help='Number of threads (for parallel version)')
    
    args = parser.parse_args()
    
    # Clean up previous output files
    cleanup_previous_outputs()
    
    measure_app_power(args.app_type, None, args.threads)

if __name__ == "__main__":
    main()

