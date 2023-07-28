import argparse
from pathlib import Path

import cv2
import numpy as np
from sklearn.cluster import KMeans
import turtle

# Clustering 
def generate_clusters(pixels):
  coords = np.vstack((pixels[0], pixels[1])).T
  kmeans = KMeans(n_clusters=30).fit(coords)
  clusters = kmeans.predict(coords)
  return clusters

# Gcode generation
def generate_gcode(image, clusters):
  
  pixels = np.where(image > 128)
  coords = np.vstack((pixels[0], pixels[1])).T
  
  gcode = []
  for i in range(clusters.max()+1):
    cluster_coords = coords[clusters == i]
    x, y = cluster_coords[0]
    gcode.append(f"G0 X{x} Y{y}")
    
    for x, y in cluster_coords[1:]:
      gcode.append(f"G1 X{x} Y{y}")
      
  return gcode
  
# Gcode plotting  
def plot_gcode(commands):

  prev_cluster = None
  
  for command, x, y in commands:

    # Get cluster 
    if "(" in command:
      current_cluster = int(command.split("(")[1].split(")")[0])
    else:
      current_cluster = 0
    
    if current_cluster != prev_cluster:
        turtle.penup()

    if command.startswith("G1"):
        turtle.pendown()

    turtle.goto(x, y)  

    prev_cluster = current_cluster
   
# Main function
if __name__ == "__main__":

  # Parse args
  parser = argparse.ArgumentParser()
  parser.add_argument("image_path")
  parser.add_argument("gcode_path")
  args = parser.parse_args()

  # Process image
  img = cv2.imread(args.image_path, 0)
  image = cv2.Canny(img, 100, 200)

  # Cluster pixels
  clusters = generate_clusters(np.where(image > 128))
  
  # Generate gcode
  gcode = generate_gcode(image, clusters)
  
  # Save gcode file
  with open(args.gcode_path, "w") as f:
    f.write("\n".join(gcode))
    
  # Plot
  # commands = [(c.split(" ")[0], float(c.split("X")[1].split(" ")[0]), 
  #             float(c.split("Y")[1])) for c in gcode]
  commands = []
  for c in gcode:
    try: 
      x = float(c.split("X")[1].split(" ")[0])
      y = float(c.split("Y")[1]) 
      commands.append((c.split(" ")[0], x, y))
    except (IndexError, ValueError):
      continue
  plot_gcode(commands)