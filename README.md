# Image Color Sampler

## Overview

Image Color Sampler is a graphical application that allows users to sample colors from an uploaded image. Users can select multiple colors, view the selected colors, and calculate the average color. The application supports zooming and panning on the image for precise color selection. The intent is to choose a color from a range of values when its from an unreliable source. The reason this was made was to sample colors for cartoon characters in a TV broadcast. Since the colors can vary quite a bit across the low fidelity images that sometimes comes from a broadcast transfer, this gives a way to find an approximate smooth value.

## Features

- Upload and display an image for color sampling.
- Click on the image to sample colors. (can sample up to 64 times)
- Display sampled colors and their hexadecimal values.
- Calculate and display the average color of the sampled colors.
- Zoom in and out using the mouse wheel.
- Pan the image using the middle mouse button.
- Clear all sampled colors.
- Delete individual sampled colors.
- Automatically create a virtual environment for running the application.
- Portable Miniconda installation for isolated environment management.

## Requirements

- Windows operating system.
- Internet connection for downloading Miniconda (if not already installed).

## Installation and Usage (WINDOWS)

1. **Download and extract the project:**
   - Download and extract the contents of the project to a directory on your computer.

2. **Run the application:**
   - Double-click the `setup_and_run.bat` file to set up the virtual environment and run the application. The command prompt will be minimized during execution.

## File Structure

- `setup_and_run.bat`: Main batch script for setting up the environment and running the application.
- `avg_color_palette_sampler.py`: Main Python script for the Image Color Sampler application.
- `miniconda3/`: Directory for the local Miniconda installation (automatically created).

## Usage Instructions

1. **Upload an Image:**
   - Click the "Open Image" button to select and upload an image for sampling.

2. **Sample Colors:**
   - Click on the image to sample colors. The sampled colors and their hexadecimal values will be displayed on the right.

3. **Zoom and Pan:**
   - Use the mouse wheel to zoom in and out of the image.
   - Press and hold the middle mouse button to pan the image.

4. **Clear Colors:**
   - Click the "Clear Colors" button to remove all sampled colors.

5. **Delete a Color:**
   - Click the "X" button next to a sampled color to delete it.

6. **View Average Color:**
   - The average color of the sampled colors is displayed at the top right.

## Troubleshooting

- Ensure you have an active internet connection for the initial setup if Miniconda is not installed locally.
- If the application does not start, ensure that the `setup_and_run.bat` script has the necessary permissions to execute.
- if you still have issues and have a venv and/or miniconda3 directory, delete those and run the `setup_and_run.bat` script.

## License

This project is licensed under the MIT License.
