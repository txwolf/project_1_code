import os
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata, Rbf, SmoothBivariateSpline
from pykrige.ok import OrdinaryKriging
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.tri as tri
from scipy.spatial import Delaunay

def inverse_distance_weighting(x, y, z, xi, yi, power=2):
    zi = np.zeros_like(xi)
    for i in range(xi.shape[0]):
        for j in range(xi.shape[1]):
            dist = np.sqrt((x - xi[i, j])**2 + (y - yi[i, j])**2)
            weights = 1 / (dist ** power)
            zi[i, j] = np.sum(weights * z) / np.sum(weights)
    return zi

# Function for natural neighbor interpolation
def natural_neighbor(x, y, z, xi, yi):
    tri_data = tri.Triangulation(x, y)
    interpolator = tri.LinearTriInterpolator(tri_data, z)
    zi = interpolator(xi, yi)
    return zi

def delaunay_triangulation(x, y, z, xi, yi):
    # Perform Delaunay triangulation
    tri_data = Delaunay(np.array([x, y]).T)
    
    # Convert to matplotlib.tri.Triangulation object
    triangles = tri_data.simplices
    triang = tri.Triangulation(x, y, triangles)
    
    # Interpolate using LinearTriInterpolator
    interpolator = tri.LinearTriInterpolator(triang, z)
    zi = interpolator(xi, yi)
    return zi

class GridFileConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Grid File Converter")

        self.file_path = ""
        self.df = None
        self.columns = []

        self.create_widgets()

    def create_widgets(self):
        # File selection
        self.file_label = tk.Label(self.root, text="Select CSV File:", anchor='w')
        self.file_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.file_button = tk.Button(self.root, text="Browse", command=self.browse_file)
        self.file_button.grid(row=0, column=1, padx=10, pady=10, sticky='w')

        self.file_entry = tk.Entry(self.root, width=50)
        self.file_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='w')

        # Column selection
        self.x_label = tk.Label(self.root, text="X Column:", anchor='w')
        self.x_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.x_var = tk.StringVar()
        self.x_menu = tk.OptionMenu(self.root, self.x_var, '')
        self.x_menu.grid(row=2, column=1, padx=10, pady=10, sticky='w')

        self.y_label = tk.Label(self.root, text="Y Column:", anchor='w')
        self.y_label.grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.y_var = tk.StringVar()
        self.y_menu = tk.OptionMenu(self.root, self.y_var, '')
        self.y_menu.grid(row=3, column=1, padx=10, pady=10, sticky='w')

        self.z_label = tk.Label(self.root, text="Z Column:", anchor='w')
        self.z_label.grid(row=4, column=0, padx=10, pady=10, sticky='w')
        self.z_var = tk.StringVar()
        self.z_menu = tk.OptionMenu(self.root, self.z_var, '')
        self.z_menu.grid(row=4, column=1, padx=10, pady=10, sticky='w')

        # Grid method
        self.method_label = tk.Label(self.root, text="Grid Method:", anchor='w')
        self.method_label.grid(row=5, column=0, padx=10, pady=10, sticky='w')
        self.method_var = tk.StringVar(value="linear")
        self.method_menu = tk.OptionMenu(self.root, self.method_var, "linear", "nearest", "cubic", "kriging", "thin_plate", "idw", "biharmonic", "natural_neighbor", "delaunay")
        self.method_menu.grid(row=5, column=1, padx=10, pady=10, sticky='w')

        # Cell size
        self.cell_size_label = tk.Label(self.root, text="Cell Size:", anchor='w')
        self.cell_size_label.grid(row=6, column=0, padx=10, pady=10, sticky='w')
        self.cell_size_entry = tk.Entry(self.root, width=20)
        self.cell_size_entry.grid(row=6, column=1, padx=10, pady=10, sticky='w')
        self.cell_size_entry.insert(0, "0.001")

        # Blanking value
        self.blanking_label = tk.Label(self.root, text="Blanking Value:", anchor='w')
        self.blanking_label.grid(row=7, column=0, padx=10, pady=10, sticky='w')
        self.blanking_entry = tk.Entry(self.root, width=20)
        self.blanking_entry.grid(row=7, column=1, padx=10, pady=10, sticky='w')
        self.blanking_entry.insert(0, "-9999")

        # Visualization option
        self.visualize_var = tk.IntVar(value=1)
        self.visualize_check = tk.Checkbutton(self.root, text="Visualize Output", variable=self.visualize_var)
        self.visualize_check.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky='w')

        # Process button
        self.process_button = tk.Button(self.root, text="Process", command=self.process_file)
        self.process_button.grid(row=9, column=1, padx=10, pady=10, sticky='w')

    def browse_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, self.file_path)
        if self.file_path:
            self.df = pd.read_csv(self.file_path)
            self.columns = list(self.df.columns)
            self.update_column_menus()
            messagebox.showinfo("File Loaded", "CSV file loaded successfully!")

    def update_column_menus(self):
        menu = self.x_menu["menu"]
        menu.delete(0, "end")
        for col in self.columns:
            menu.add_command(label=col, command=tk._setit(self.x_var, col))

        menu = self.y_menu["menu"]
        menu.delete(0, "end")
        for col in self.columns:
            menu.add_command(label=col, command=tk._setit(self.y_var, col))

        menu = self.z_menu["menu"]
        menu.delete(0, "end")
        for col in self.columns:
            menu.add_command(label=col, command=tk._setit(self.z_var, col))

    def process_file(self):
        if not self.file_path or not isinstance(self.df, pd.DataFrame):
            messagebox.showerror("Error", "Please select a valid CSV file.")
            return

        x_col = self.x_var.get()
        y_col = self.y_var.get()
        z_col = self.z_var.get()
        method = self.method_var.get()
        cell_size = float(self.cell_size_entry.get())
        blanking = float(self.blanking_entry.get())

        try:
            data = self.df[[x_col, y_col, z_col]].copy()
            data.columns = ['X', 'Y', 'Z']
            data = data.dropna(subset=['X', 'Y', 'Z'])

            if data.empty:
                messagebox.showerror("Error", "No valid data points found after removing NaNs.")
                return

            xi, yi, zi = self.grid_data(data, method, cell_size, blanking)

            # Create output file name with -grid-output suffix and current datetime
            input_filename = os.path.splitext(os.path.basename(self.file_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_file = f"{input_filename}-grid-output-{timestamp}.xyz"

            self.save_grid_to_xyz(xi, yi, zi, output_file)

            if self.visualize_var.get():
                self.visualize_grid(xi, yi, zi, z_col, x_col, y_col)

            messagebox.showinfo("Success", f"Grid file saved to {output_file} and visualized successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def grid_data(self, df, method, cell_size, blanking):
        x = df['X'].values
        y = df['Y'].values
        z = df['Z'].values

        xi = np.arange(x.min(), x.max(), cell_size)
        yi = np.arange(y.min(), y.max(), cell_size)
        xi, yi = np.meshgrid(xi, yi)

        if method == 'thin_plate':
            # Using RBF for thin_plate (interpreted as minimum curvature)
            rbf = Rbf(x, y, z, function='thin_plate')
            zi = rbf(xi, yi)
        elif method == 'kriging':
            # Using pykrige for kriging (interpreted as minimum curvature)
            OK = OrdinaryKriging(x, y, z, variogram_model="spherical")
            zi, ss = OK.execute("grid", xi[0], yi[:, 0])
        elif method == 'idw':
            # Inverse Distance Weighting
            zi = inverse_distance_weighting(x, y, z, xi, yi)
        elif method == 'biharmonic':
        # Biharmonic spline interpolation with error handling
            try:
                spline = SmoothBivariateSpline(x, y, z)
                zi = spline(xi[:, 0], yi[0, :])
            except Exception as e:
                messagebox.showerror("Error", f"Biharmonic spline interpolation failed: {e}")
                return None, None, None    
        elif method == 'natural_neighbor':
            zi = natural_neighbor(x, y, z, xi, yi)
        elif method == 'delaunay':
            zi = delaunay_triangulation(x, y, z, xi, yi)
        else:
            # Using scipy griddata for other methods
            zi = griddata((x, y), z, (xi, yi), method=method)

        zi[np.isnan(zi)] = blanking
        return xi, yi, zi

    def save_grid_to_xyz(self, xi, yi, zi, output_file):
        rows, cols = xi.shape
        with open(output_file, 'w') as f:
            for i in range(rows):
                for j in range(cols):
                    f.write(f"{xi[i, j]} {yi[i, j]} {zi[i, j]}\n")

    def visualize_grid(self, xi, yi, zi, z_label, x_label, y_label):
        plt.scatter(xi, yi, c=zi, cmap='viridis', marker='o')
        plt.colorbar(label=z_label)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title('Gridded Data Visualization')
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = GridFileConverter(root)
    root.mainloop()
