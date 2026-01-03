# ArcGIS Pro Map and Layout Programming

This repository contains reusable Python functions for programmatic creation
and control of maps and layouts in ArcGIS Pro using the ArcPy API.

## Repository Structure
- `functions.py` — defines reusable functions for map and layout automation
- `usage_example.py` — demonstrates how to use the functions on a sample dataset

## Functions

- `create_single_map(...)`  
  Creates a map and applies user-defined symbology to a spatial layer.  
  Inputs include map name, data path, renderer type, attribute field, color ramp,
  and optional classification and labeling parameters.

- `create_standard_layout(...)`  
  Generates a standardized layout for a given map with configurable title text,
  map extent, legend placement, scale bar, and north arrow positioning.

## Requirements
- ArcGIS Pro
- ArcPy (installed with ArcGIS Pro)
- Python 3.x (ArcGIS Pro environment)

## Usage
1. Create an empty ArcGIS Pro project (`.aprx`).
2. Update file paths and parameters in `usage_example.py`.
3. Run the script using the ArcGIS Pro Python environment.
