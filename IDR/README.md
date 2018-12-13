![img](https://github.com/Daikon-Sun/Routing-Visualization/raw/master/IDR/IDR.png)
*Example visualization by 3d_visualize.py.*

# Visualization Tool for Initial Detailed Routing

## Required Packages and Versions
- python3 >= 3.6
- numpy
- **matplotlib**

## File Descriptions
- 3d_visiualize.py: 3-dimensional visualization.

## Input File Format
The file format is defined as:
```
net_name
(
x0 y0 z0 [x1 y1 z1]
...
)
```
Use three numbers to denote a point and six numbers to denote anything else.

For obstalces, tracks, or anything else that does not belong to a net, use '\_\_ALL\_\_' to replace net_name.

Example file formats can be found in the directory `example`.

## Usage
```
python3 3d_visualize.py filename [net_name1 net_name2 ...]
```
[net_name1, net_name2 ...] is the subset of all nets that you want to visualize.
If the subset is empty, all nets will be considered.

Use right mouse button to zoom in/out and left mouse button to rotate.

## Setup
There is a dictionary in the file named *vis*, and you have to first set up the entries in *vis*.
The program will read several input files according to the list of 'name's in *vis*.

That is, the input filenames will be [filename + '.' + 'name1', filename + '.' + 'name2', ...].

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
python3 3d_visualize.py example/example net1230
```

## Additional Informations
Because 3d_visualize uses **matplotlib**, it cannot handle very-large scale inputs.

It is suitable for inputs with less than 10^5~10^6 items (i.e. lines of text).
