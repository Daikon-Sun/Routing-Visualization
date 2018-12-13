# Visualization Tool for Bus Routing

## Required Packages and Versions

- python3 >= 3.6
- pyqtgraph >= 0.10.0
- PyQt5 >= 5.11.2
- numpy
- matplotlib

## File Descriptions

- 2d_visiualize.py: 2-dimensional visualization that trys to mimic the style of Cadence Innovus.
- 3d_visiualize.py: 3-dimensional visualization.

## Usage

### File Format
The file format is defined as:
```
bus_name bit_name
(
x0 y0 z0 [x1 y1 z1]
...
)
```
Use three numbers to denote a point and six numbers to denote anything else.

For obstalces, tracks, or anything else that does not belong to a bus and bit,
use '\_\_ALL\_\_' to replace bus_name and bit_name.

Example file formats can be found in the direction `example`.

### 2d_visualize
There is a dictionary in the file named *vis*.

Your have to first set up the entries in *vis*.

Each entry in *vis* is formatted as: 
```
'name' : (On/OFF, linewidth, symbol).
```
- 'name': the description of the set of objects,
- On/OFF: True or False that determined if the program is going to visualize 'name'
- symbol: for point objects, choose on symbol from {'o', 't', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd'}. For example, 'o' is a circle and 't' is a triangle.

```
python3 2d_visualize.py file_name [bus_name1 busname_2 ...]
```
[bus_name1, bus_name2 ...] is the subset of all buses that you want to visualize.
If the subset is empty, all buses will be considered.

Use scroll wheel to zoom in/out and left mouse button to drag around.

### 3d_visualize
```
python3 3d_visualize.py file_name [bus_name1 busname_2 ...]
```
[bus_name1, bus_name2 ...] is the subset of all buses that you want to visualize.

Use right mouse button to zoom in/out and left mouse button to rotate.
