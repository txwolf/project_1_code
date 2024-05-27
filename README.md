# Grid File Converter

Grid File Converter is a Python application that allows users to convert CSV files into gridded data files. It supports multiple interpolation methods including linear, nearest, cubic, kriging, and thin plate splines.

## Features

- Select CSV files and specify columns for X, Y, and Z values.
- Choose from multiple grid interpolation methods.
- Specify cell size and blanking value.
- Option to visualize the output grid.

## Prerequisites

- Python 3.6 or later
- Virtual environment (recommended)

## Installation

1. **Clone the Repository**

   ```bash
   git clone <your-repository-url>
   cd <repository-folder>
   ```

2. **Set Up a Virtual Environment**

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**

   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Application**

   ```bash
   python grid-converter.py
   ```

2. **Use the GUI to:**

   - Select a CSV file.
   - Choose columns for X, Y, and Z values.
   - Select the grid interpolation method.
   - Specify cell size and blanking value.
   - Optionally visualize the output grid.

## File Structure

- `grid-converter.py`: The main application script.
- `requirements.txt`: List of dependencies.

## Dependencies

- numpy
- pandas
- scipy
- matplotlib
- pykrige

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License.
