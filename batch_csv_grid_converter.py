import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import os
from datetime import datetime

class ParameterWindow:
    def __init__(self, master, file_path, columns, add_callback):
        self.master = master
        self.file_path = file_path
        self.add_callback = add_callback

        self.window = tk.Toplevel(master)
        self.window.title(f"Parameters for {os.path.basename(file_path)}")

        tk.Label(self.window, text="X Column:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.x_var = tk.StringVar()
        self.x_menu = ttk.Combobox(self.window, textvariable=self.x_var, values=columns)
        self.x_menu.grid(row=0, column=1, padx=10, pady=5, sticky='w')

        tk.Label(self.window, text="Y Column:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.y_var = tk.StringVar()
        self.y_menu = ttk.Combobox(self.window, textvariable=self.y_var, values=columns)
        self.y_menu.grid(row=1, column=1, padx=10, pady=5, sticky='w')

        tk.Label(self.window, text="Z Column:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.z_var = tk.StringVar()
        self.z_menu = ttk.Combobox(self.window, textvariable=self.z_var, values=columns)
        self.z_menu.grid(row=2, column=1, padx=10, pady=5, sticky='w')

        tk.Label(self.window, text="Grid Method:").grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self.method_var = tk.StringVar(value="linear")
        self.method_menu = ttk.Combobox(self.window, textvariable=self.method_var, values=["linear", "nearest", "cubic"])
        self.method_menu.grid(row=3, column=1, padx=10, pady=5, sticky='w')

        tk.Label(self.window, text="Cell Size:").grid(row=4, column=0, padx=10, pady=5, sticky='w')
        self.cell_size_entry = tk.Entry(self.window)
        self.cell_size_entry.insert(0, "0.25")
        self.cell_size_entry.grid(row=4, column=1, padx=10, pady=5, sticky='w')

        tk.Label(self.window, text="Blanking:").grid(row=5, column=0, padx=10, pady=5, sticky='w')
        self.blanking_entry = tk.Entry(self.window)
        self.blanking_entry.insert(0, "0.25")
        self.blanking_entry.grid(row=5, column=1, padx=10, pady=5, sticky='w')

        self.set_default_values(columns)

        tk.Button(self.window, text="Add", command=self.add_to_tree).grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    def set_default_values(self, columns):
        x_default = next((col for col in columns if "easting" in col.lower()), None)
        y_default = next((col for col in columns if "northing" in col.lower()), None)

        self.x_var.set(x_default)
        self.y_var.set(y_default)
        self.z_var.set("")

    def add_to_tree(self):
        x_col = self.x_var.get()
        y_col = self.y_var.get()
        z_col = self.z_var.get()
        method = self.method_var.get()
        cell_size = self.cell_size_entry.get()
        blanking = self.blanking_entry.get()

        if not x_col or not y_col or not z_col or not method or not cell_size or not blanking:
            messagebox.showerror("Error", "All fields must be filled out.")
            return

        self.add_callback(self.file_path, x_col, y_col, z_col, method, cell_size, blanking, "Loaded")
        self.window.destroy()

class GridFileConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Grid File Converter")

        self.files = []
        self.create_widgets()

    def create_widgets(self):
        # Add Files and Clear All buttons at the top
        self.add_file_button = tk.Button(self.root, text="Add Files", command=self.add_files)
        self.add_file_button.grid(row=0, column=0, padx=(10, 5), pady=10, sticky='w')

        self.clear_button = tk.Button(self.root, text="Clear All", command=self.clear_all_files)
        self.clear_button.grid(row=0, column=1, padx=(5, 10), pady=10, sticky='w')

        # Treeview to display the files and their parameters
        self.tree = ttk.Treeview(self.root, columns=("File", "X Column", "Y Column", "Z Column", "Grid Method", "Cell Size", "Blanking", "Status"), show="headings")
        self.tree.heading("File", text="File")
        self.tree.heading("X Column", text="X Column")
        self.tree.heading("Y Column", text="Y Column")
        self.tree.heading("Z Column", text="Z Column")
        self.tree.heading("Grid Method", text="Grid Method")
        self.tree.heading("Cell Size", text="Cell Size")
        self.tree.heading("Blanking", text="Blanking")
        self.tree.heading("Status", text="Status")

        self.tree.column("File", width=200)
        self.tree.column("X Column", width=100)
        self.tree.column("Y Column", width=100)
        self.tree.column("Z Column", width=100)
        self.tree.column("Grid Method", width=100)
        self.tree.column("Cell Size", width=100)
        self.tree.column("Blanking", width=100)
        self.tree.column("Status", width=100)

        self.tree.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

        # Summary label under the table, moved to the right
        self.summary_label = tk.Label(self.root, text="No files loaded.")
        self.summary_label.grid(row=2, column=3, padx=10, pady=5, sticky='e')

        # Progress bar
        self.progress = ttk.Progressbar(self.root, length=400, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=5, padx=10, pady=10, sticky='w')

        # Process All button at the bottom-right corner
        self.process_button = tk.Button(self.root, text="Process All", command=self.process_all_files)
        self.process_button.grid(row=3, column=3, padx=10, pady=10, sticky='e')

    def add_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("CSV Files", "*.csv")])
        if not file_paths:
            return

        for file_path in file_paths:
            df = pd.read_csv(file_path)
            columns = list(df.columns)
            self.files.append((file_path, df))

            ParameterWindow(self.root, file_path, columns, self.add_to_tree)

        self.update_summary()

    def add_to_tree(self, file_path, x_col, y_col, z_col, method, cell_size, blanking, status):
        self.tree.insert("", "end", values=(file_path, x_col, y_col, z_col, method, cell_size, blanking, status))

    def update_summary(self):
        total_files = len(self.files)
        total_size = sum(os.path.getsize(file[0]) for file in self.files) / (1024 * 1024)  # size in MB
        self.summary_label.config(text=f"Loaded {total_files} file(s), {total_size:.2f} MB")

    def process_all_files(self):
        if not self.tree.get_children():
            messagebox.showwarning("Warning", "No files added. Please add files to process.")
            return

        total_files = len(self.tree.get_children())
        self.progress["maximum"] = total_files

        for i, item in enumerate(self.tree.get_children(), 1):
            values = self.tree.item(item, "values")
            file_path, x_col, y_col, z_col, method, cell_size, blanking, status = values
            
            self.tree.item(item, values=(file_path, x_col, y_col, z_col, method, cell_size, blanking, "Processing..."))
            self.root.update_idletasks()  # Update UI to show the pending status

            df = pd.read_csv(file_path)

            try:
                data = df[[x_col, y_col, z_col]].copy()
                data.columns = ['X', 'Y', 'Z']
                data.dropna(subset=['X', 'Y', 'Z'], inplace=True)

                if data.empty:
                    messagebox.showerror("Error", f"No valid data points found in {file_path} after removing NaNs.")
                    self.tree.item(item, values=(file_path, x_col, y_col, z_col, method, cell_size, blanking, "Error"))
                    continue

                xi, yi, zi = self.grid_data(data, method, float(cell_size), float(blanking))

                input_filename = os.path.splitext(os.path.basename(file_path))[0]
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                output_file = f"{input_filename}-grid-output-{timestamp}.xyz"

                self.save_grid_to_xyz(xi, yi, zi, output_file)
                self.tree.item(item, values=(file_path, x_col, y_col, z_col, method, cell_size, blanking, "Completed"))

            except Exception as e:
                messagebox.showerror("Error", f"Error processing {file_path}: {str(e)}")
                self.tree.item(item, values=(file_path, x_col, y_col, z_col, method, cell_size, blanking, "Error"))

            self.progress["value"] = i
            self.root.update_idletasks()  # Update progress bar

        messagebox.showinfo("Info", "All files processed successfully.")

    def grid_data(self, df, method, cell_size, blanking):
        x = df['X']
        y = df['Y']
        z = df['Z']

        xi = np.arange(x.min(), x.max(), cell_size)
        yi = np.arange(y.min(), y.max(), cell_size)
        xi, yi = np.meshgrid(xi, yi)

        zi = griddata((x, y), z, (xi, yi), method=method)
        zi[np.isnan(zi)] = blanking

        return xi, yi, zi

    def save_grid_to_xyz(self, xi, yi, zi, output_file):
        rows, cols = xi.shape
        with open(output_file, 'w') as f:
            for i in range(rows):
                for j in range(cols):
                    f.write(f"{xi[i, j]} {yi[i, j]} {zi[i, j]}\n")

    def clear_all_files(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.files.clear()
        self.progress["value"] = 0
        self.update_summary()

if __name__ == "__main__":
    root = tk.Tk()
    app = GridFileConverter(root)
    root.mainloop()
