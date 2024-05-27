import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import argparse

def read_csv(file_path, x_col, y_col, z_col):
    df = pd.read_csv(file_path)
    
    # Convert column indices to integers if they are numeric
    try:
        x_col = int(x_col)
        y_col = int(y_col)
        z_col = int(z_col)
        df = df.iloc[:, [x_col, y_col, z_col]]
    except ValueError:
        df = df[[x_col, y_col, z_col]]

    df.columns = ['X', 'Y', 'Z']  # Rename columns for consistency
    df.dropna(subset=['X', 'Y', 'Z'], inplace=True)  # Remove rows with NaNs in X, Y, or Z
    return df

def grid_data(df, method, cell_size, blanking):
    # Extract coordinates and values
    x = df['X']
    y = df['Y']
    z = df['Z']
    
    # Define grid
    xi = np.arange(x.min(), x.max(), cell_size)
    yi = np.arange(y.min(), y.max(), cell_size)
    xi, yi = np.meshgrid(xi, yi)
    
    # Perform grid interpolation
    zi = griddata((x, y), z, (xi, yi), method=method)
    
    # Apply blanking
    zi[np.isnan(zi)] = blanking
    
    return xi, yi, zi

def save_grid_to_xyz(xi, yi, zi, output_file):
    rows, cols = xi.shape
    with open(output_file, 'w') as f:
        for i in range(rows):
            for j in range(cols):
                f.write(f"{xi[i, j]} {yi[i, j]} {zi[i, j]}\n")

def main(input_file, output_file, x_col, y_col, z_col, method, cell_size, blanking):
    # Read the CSV file
    df = read_csv(input_file, x_col, y_col, z_col)
    
    # Check if the dataframe is empty after dropping NaNs
    if df.empty:
        print("No valid data points found after removing NaNs.")
        return
    
    # Grid the data
    xi, yi, zi = grid_data(df, method, cell_size, blanking)
    
    # Save to XYZ format
    save_grid_to_xyz(xi, yi, zi, output_file)
    print(f"Grid file saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert CSV to Grid File (XYZ format)")
    parser.add_argument("input_file", help="Path to the input CSV file")
    parser.add_argument("output_file", help="Path to the output XYZ file")
    parser.add_argument("--x_col", required=True, help="Column name or index for the X positions (northing)")
    parser.add_argument("--y_col", required=True, help="Column name or index for the Y positions (easting)")
    parser.add_argument("--z_col", required=True, help="Column name or index for the Z values (VG_RES)")
    parser.add_argument("--method", choices=["linear", "nearest", "cubic"], default="linear", help="Gridding method (linear, nearest, cubic)")
    parser.add_argument("--cell_size", type=float, default=1.0, help="Cell size for the grid")
    parser.add_argument("--blanking", type=float, default=np.nan, help="Value to use for blanking (NaNs in the output grid)")
    
    args = parser.parse_args()
    
    try:
        main(args.input_file, args.output_file, args.x_col, args.y_col, args.z_col, args.method, args.cell_size, args.blanking)
    except IndexError as e:
        print(f"Error: {e}. Please check that the column indices are within the valid range.")
    except KeyError as e:
        print(f"Error: {e}. Please check that the column names are correct.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
