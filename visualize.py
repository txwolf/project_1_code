import matplotlib.pyplot as plt
import numpy as np

# Load the XYZ file
data = np.loadtxt('output.xyz')

# Extract columns
x = data[:, 0]
y = data[:, 1]
z = data[:, 2]

# Create a scatter plot
plt.scatter(x, y, c=z, cmap='viridis', marker='o')
plt.colorbar(label='VG_RES')
plt.xlabel('Easting')
plt.ylabel('Northing')
plt.title('Gridded Data Visualization')
plt.show()