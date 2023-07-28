import argparse
import logging
from pathlib import Path

import cv2
import numpy as np
import turtle
from PIL import Image

logger = logging.getLogger(__name__)

def process_image(img_path: Path) -> np.ndarray:
    """Process image to binary for CNC."""
    img = cv2.imread(str(img_path), 0)
    processed_img = cv2.Canny(img, 100, 200)
    return processed_img

def generate_gcode(processed_image: np.ndarray) -> list[str]:
    """Generate GCode commands from processed image."""
    pixels = np.where(processed_image > 128)
    commands = [f"G1 X{x} Y{y}" for x, y in zip(pixels[0], pixels[1])]
    return commands

def write_gcode(gcode: list[str], gcode_path: Path):
    """Write GCode commands to file."""
    with gcode_path.open("w") as f:
        f.write("\n".join(gcode))

def parse_gcode(gcode_path: Path) -> list[tuple]:
    """Parse GCode file into list of commands."""
    commands = []
    with gcode_path.open("r") as f:
        for line in f:
            if line.startswith("G1"):
                x = float(line.split("X")[1].split(" ")[0]) 
                y = float(line.split("Y")[1].split(" ")[0])
                commands.append(("G1", x, y))
    return commands

def plot_gcode(commands: list[tuple]):
    """Plot GCode commands using turtle."""
    turtle.speed(100)
    for command, x, y in commands:
        if command == "G1": 
            turtle.goto(x, y)
    turtle.done()

def main(args):
    img_path = Path(args.image_path)
    gcode_path = Path(args.gcode_path)
    
    processed_image = process_image(img_path)  
    gcode = generate_gcode(processed_image)
    write_gcode(gcode, gcode_path)
    
    parsed_commands = parse_gcode(gcode_path)
    plot_gcode(parsed_commands)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image_path", required=True, help="Path to input image")
    parser.add_argument("-o", "--gcode_path", required=True, help="Output gcode path")
    args = parser.parse_args()
    
    main(args)