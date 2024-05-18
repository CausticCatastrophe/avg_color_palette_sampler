# Image Color Sampler

## Overview

Image Color Sampler is a graphical application that allows users to sample colors from an uploaded image. Users can select multiple colors, view the selected colors, and calculate the average color. The application supports zooming and panning on the image for precise color selection. The intent is to choose a color from a range of values when it’s from an unreliable source. This was made to sample colors for cartoon characters in a TV broadcast, where colors can vary across low fidelity images from a broadcast transfer, providing a way to find an approximate smooth value.

## Features

- Upload and display an image for color sampling.
- Click and drag on the image to select a region for color sampling.
- Calculate the median absolute deviation to filter outliers from the sampled colors.
- Average the remaining colors after filtering outliers.
- Display sampled colors (up to 1024 samples).
- Calculate and display the average color of the sampled colors.
- Zoom in and out using the mouse wheel.
- Pan the image using the middle mouse button.
- Clear all sampled colors.
- Delete individual sampled colors.
- Copy colors from the palette to the clipboard.
- Save the palette to a text file.
- Save the palette as an image file.
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
- `data`: Directory for the lookup table Cel Animation Color Charts.xlsx

## Usage Instructions

1. **Upload an Image:**
   - Click the "Open Image" button to select and upload an image for sampling.

2. **Sample Colors:**
   - Click and drag on the image to select a region for sampling. The sampled colors will be averaged after filtering outliers based on the median absolute deviation.

3. **Zoom and Pan:**
   - Use the mouse wheel to zoom in and out of the image.
   - Press and hold the middle mouse button to pan the image.

4. **Clear Colors:**
   - Click the "Clear Colors" button to remove all sampled colors.

5. **Delete a Color:**
   - Click on a sampled color to delete it.

6. **View Average Color:**
   - The average color of the sampled colors is displayed at the top right.

7. **Quantize to STAC Chart colors:**
   - Can optionally quantize to the STAC Chart colors found in lookup table.

8. **Add to Palette:**
   - Click the "Add to Palette" button to add the average color to the palette. This will clear the current sampled colors.

9. **Copy Color to Clipboard:**
   - Click on a color in the palette to copy its hexadecimal value to the clipboard.

10. **Save Palette to Text File:**
   - Click the "Save Palette" button to save the palette to a text file. Each color will be saved in hexadecimal format, one per line.

11. **Save Palette as Image:**
    - Click the "Save Palette as Image" button to save the palette as a PNG image. Each color will be displayed as a wide rectangle bar with the hexadecimal value written next to it.

## Troubleshooting

- Ensure you have an active internet connection for the initial setup if Miniconda is not installed locally.
- If the application does not start, ensure that the `setup_and_run.bat` script has the necessary permissions to execute.
- If issues persist and you have a `venv` and/or `miniconda3` directory, delete those and run the `setup_and_run.bat` script again.

## License

This project is licensed under the MIT License.
