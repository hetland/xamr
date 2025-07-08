#!/usr/bin/env python3
"""
Basic example of using xamr to analyze AMReX plot files
"""

import sys
import os

# Add the parent directory to the path so we can import xamr
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import xamr
    
    def main():
        # Example AMReX plot file (you'll need to provide your own)
        plot_file = 'plt00100'  # Replace with your actual plot file
        
        if not os.path.exists(plot_file):
            print(f"Plot file {plot_file} not found.")
            print("Please update the plot_file variable with a valid AMReX plot file.")
            return
        
        # Load the dataset
        print(f"Loading {plot_file}...")
        ds = xamr.open_amrex(plot_file)
        
        # Display basic information
        print(f"Dataset attributes:")
        print(f"  Max level: {ds.attrs['max_level']}")
        print(f"  Dimensionality: {ds.attrs['dimensionality']}")
        print(f"  Current time: {ds.attrs['current_time']}")
        print(f"  Domain dimensions: {ds.attrs['domain_dimensions']}")
        
        # List available data variables
        print(f"\nAvailable data variables:")
        for var in ds.data_vars:
            print(f"  {var}")
        
        # Example: work with temperature field (if available)
        if 'temperature' in ds.data_vars:
            print(f"\nAnalyzing temperature field...")
            temp = ds['temperature']
            
            print(f"  Mean temperature: {temp.mean():.2f}")
            print(f"  Max temperature: {temp.max():.2f}")
            print(f"  Min temperature: {temp.min():.2f}")
            
            # Calculate gradient
            temp_grad_x = ds.calc.gradient('temperature', 'x')
            print(f"  Mean temperature gradient (x): {temp_grad_x.mean():.2e}")
            
            # Level selection example
            if ds.attrs['max_level'] > 0:
                temp_finest = temp.level_select(ds.attrs['max_level'])
                print(f"  Mean temperature (finest level): {temp_finest.mean():.2f}")
        
        # Example: work with velocity fields (if available)
        if 'x_velocity' in ds.data_vars and 'y_velocity' in ds.data_vars:
            print(f"\nAnalyzing velocity fields...")
            
            # Calculate vorticity
            vorticity = ds.calc.vorticity('x_velocity', 'y_velocity')
            print(f"  Mean vorticity: {vorticity.mean():.2e}")
            print(f"  Max vorticity: {vorticity.max():.2e}")
            
            # Calculate divergence
            divergence = ds.calc.divergence('x_velocity', 'y_velocity')
            print(f"  Mean divergence: {divergence.mean():.2e}")
        
        print(f"\nAnalysis complete!")
        
except ImportError as e:
    print(f"Error importing xamr: {e}")
    print("Make sure you have installed the required dependencies:")
    print("  pip install yt numpy")
except Exception as e:
    print(f"Error: {e}")
    print("Make sure you have a valid AMReX plot file and update the plot_file variable.")

if __name__ == '__main__':
    main()
