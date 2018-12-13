![img](https://github.com/Daikon-Sun/Routing-Visualization/raw/master/BR/BR.png)
*Example visualizations by 2d_visualize.py (left) and 3d_visualize.py (right).*

# Visualization Tool for Bus Routing

## Required Packages and Versions
- python3 >= 3.6

### Python Packages
- pyqtgraph >= 0.10.0
- **PyQt5 >= 5.11.2**
- numpy
- **matplotlib**

## File Descriptions
- 2d_visiualize.py: 2-dimensional visualization that trys to mimic the style of Cadence Innovus.
- 3d_visiualize.py: 3-dimensional visualization.

## Input File Format
The file format is defined as:
```
bus_name bit_name
(
x0 y0 z0 [x1 y1 z1]
...
)
```
Use three numbers to denote a point and six numbers to denote anything else.

For obstalces, tracks, or anything else that does not belong to a bus and bit, use a unified name for simplicity.
For example, use '\_\_ALL\_\_' to replace bus_name and 'ALL' to bit_name.

Example file formats can be found in the directory `example`.

## Usage
```
python3 {} filename [bus_name1 bus_name2 ...]
```
[bus_name1, bus_name2 ...] is the subset of all buses that you want to visualize.
If the subset is empty, all buses will be considered.

### 2d_visualize.py
Use scroll wheel to zoom in/out and left mouse button to drag around.

Double click on anywhere to unveil the information at the clicked coordinates.

### 3d_visualize.py
Use right mouse button to zoom in/out and left mouse button to rotate.

## Setup
There is a dictionary in the file named *vis*, and you have to first set up the entries in *vis*.
The program will read several input files according to the list of 'name's in *vis*.

That is, the input filenames will be [filename + '.' + 'name1', filename + '.' + 'name2', ...].

### 2d_visualize.py
Each entry in *vis* is formatted as: 
```
'name' : (On/Off, linewidth, symbol)
```
- 'name': the description of the set of objects,
- On/Off: True or False that determined if the program is going to visualize 'name'
- linewidth: the linewidth for line items.
- symbol: for point items, choose one symbol from ['o', 't', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd']. For example, 'o' is a circle and 't' is a triangle.

### 3d_visualize.py
Each entry in *vis* is formatted as: 
```
'name' : (On/Off, color, alpha, linewidth)
```
- 'name': the description of the set of objects,
- On/Off: True or False that determined if the program is going to visualize 'name'
- color: a color code such as '#000000' or a function/list/tuple that accepts an integer (the z value) and returns a color code.
- alpha: 1 is opaque and 0 is transparent.
- linewidth: the linewidth for line items.

## Example
Try to type one of the followings!
```
python3 2d_visualize.py example/example
python3 2d_visualize.py example/example bus_1
python3 3d_visualize.py example/example
```

## Additional Informations
Because 3d_visualize.py uses **matplotlib**, it cannot handle very-large scale inputs.

It is suitable for inputs with less than 10^5 to 10^6 items (i.e. lines of text).

On the other hand, 2d_visualize.py uses **pyQt5**, so it's quite efficient.

It can handle inputs up to 10^7 to 10^8 items, or even 10^9 if you have great CPUs.
