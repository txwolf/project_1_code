# Grid File Converter

Grid File Converter is a Python application designed to convert CSV files into gridded data files using a graphical user interface (GUI). This tool is particularly useful for geophysical data processing, where users need to interpolate and visualize spatial data.

## Features

- Easy File Selection: Use the GUI to select CSV files easily.
- Column Specification: Specify which columns represent the X, Y, and Z values in your CSV files.
- Interpolation Method: Uses the natural neighbor interpolation method to achieve smooth, minimum curvature surfaces.
- Customizable Grid Parameters: Define cell size and blanking values.
- Batch Processing: Load multiple CSV files and process them in one go.
- Progress Indicator: Visual progress bar to track the processing of files.

## Prerequisites

- Python 3.6 or later
- Virtual environment (recommended)

## Installation

1. **Set Up a Virtual Environment**

   ```bash
   python -m venv venv
   ```

2. **Activate the Virtual Environment**

   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Application**

   ```bash
   python batch-converter.py
   ```

2. **Use the GUI to:**

   - Select a CSV files.
   - Choose columns for X, Y, and Z values.
   - Specify cell size and blanking value.
   - The application will save the gridded data to new files with a -gridded-{datetime}.xyz suffix.

## File Structure

- `batch-converter.py`: The main application script - batch convert multiple files at once.
- `converter.py`: Contains the `GridConverter` class for converting a single file.
- `requirements.txt`: List of dependencies.
- `sample-data.csv`: Contains sample CSV files for testing.

## Dependencies

- numpy
- pandas
- scipy
- matplotlib
- pykrige
