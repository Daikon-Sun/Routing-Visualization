#!/usr/bin/python3
import sys, random, re
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import CheckButtons
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from mpl_toolkits.mplot3d import Axes3D, art3d

if len(sys.argv) < 2:
    print('usage : python {} test_case_name [bus_name1 bus_name2 ...]'.format(__file__))
    print('if no bus_name is typed, all buses will be considered')
    exit()

vis_all = len(sys.argv) == 2
filename = sys.argv[1]
scale = 1
max_total_layer = 8
nrows = 2

cmap = plt.get_cmap('gist_rainbow')
layer_colors = [cmap(int(i / (max_total_layer - 1) * (cmap.N - 1))) for i in range(max_total_layer)]
layer_colors = ['white', 'blue', 'red', 'green', 'orange', 'purple', 'cyan', 'gray', 'brown']

def randColor():
    return '#' + ''.join([random.choice('0123456789ABCDEF') for i in range(6)])

#                   (On/Off, color, alpha, linewidth)
vis = {
    'obs':       (True, '#222222', 1, 2),
    'bus':       (True, layer_colors, 1, 2),
    'track':     (True, layer_colors, 1, 1)
}

bus_names = set([sys.argv[i] for i in range(2, len(sys.argv))])
bus_names.add('__ALL__')

def handle_close(event):
    plt.close('all')

fig = plt.figure(figsize=(32,18), dpi=60)
fig.canvas.mpl_connect('close_event', handle_close)
ax = fig.gca(projection='3d')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
fig.tight_layout(pad=0)
ax.autoscale(tight=True)

layer_obj_list = [[] for i in range(max_total_layer)]
max_layer = 0
obj_list = {}
bus_obj_list = dict([[bus_name, dict()] for bus_name in bus_names])
all_objs = []

def get_color(color, z):
    if isinstance(color, list):
        assert z0 == z1
        return color[z]
    elif isinstance(color, str):
        return color
    elif callable(color):
        return color()
    else:
        print('not supported!')
        exit()

def add_obj(obj, z, obj_type, busname, bitname):
    layer_obj_list[z].append((obj, len(all_objs)))
    obj_list[obj_type].append((obj, len(all_objs)))
    if bitname not in bus_obj_list[busname]:
        bus_obj_list[busname][bitname] = []
    bus_obj_list[busname][bitname].append((obj, len(all_objs)))
    all_objs.append((obj, 3))

def add_objs(xyzss, liness, rectss, obj_type, busname, bitname, color, alpha, linewidth):
    for z, (xs, ys, zs) in enumerate(xyzss):
        if len(xs) > 0:
            obj = ax.scatter(xs, ys, zs, color=get_color(color, z), alpha=alpha, linewidth=linewidth)
            add_obj(obj, z, k, busname, bitname)
    for z, lines in enumerate(liness):
        if len(lines) > 0:
            obj = ax.add_collection(Line3DCollection(lines, colors=get_color(color, z), alpha=alpha, linewidth=linewidth))
            add_obj(obj, z, k, busname, bitname)
    for z, rects in enumerate(rectss):
        if len(rects) > 0:
            coll = PatchCollection(rects, color=get_color(color, z))
            art3d.poly_collection_2d_to_3d(coll, z)
            obj = ax.add_collection(coll)
            add_obj(obj, z, k, busname, bitname)

mnx, mny, mxx, mxy = 10**99, 10**99, -10**99, -10**99
for k, v in vis.items():
    if not v[0]:
        continue
    print(k)
    obj_list[k] = []
    cur_busname = None
    for line in open(filename + '.' + k, 'r'):
        content = line.split()
        if len(content) <= 2:
            if content[0] != '(' and content[0] != ')':
                if cur_busname is not None:
                    add_objs(xyzss, liness, rectss, k, cur_busname, cur_bitname, v[1], v[2], v[3])
                xyzss = [[[], [], []] for i in range(max_total_layer)]
                liness = [[] for i in range(max_total_layer)]
                rectss = [[] for i in range(max_total_layer)]

                cur_busname = content[0]
                cur_bitname = content[1]
                if vis_all and cur_busname not in bus_names:
                    bus_names.add(cur_busname)
                    bus_obj_list[cur_busname] = dict()
                if cur_busname in bus_names and cur_bitname not in bus_obj_list[cur_busname]:
                    bus_obj_list[cur_busname][cur_bitname] = []
        else:
            assert len(content) == 6 or len(content) == 3
            if cur_busname not in bus_names:
                continue

            if len(content) == 6:
                x0 = int(content[0]) / scale
                y0 = int(content[1]) / scale
                z0 = int(content[2])
                x1 = int(content[3]) / scale
                y1 = int(content[4]) / scale
                z1 = int(content[5])
            else:
                x0 = x1 = int(content[0]) / scale
                y0 = y1 = int(content[1]) / scale
                z0 = z1 = int(content[2])

            mnx, mny, mxx, mxy = min(mnx, x0), min(mny, y0), max(mxx, x1), max(mxy, y1)

            if len(content) == 3:
                xyzss[z0][0].append(x0)
                xyzss[z0][1].append(y0)
                xyzss[z0][2].append(z0)
            elif x0 == x1 or y0 == y1:
                liness[z0].append([[x0, y0, z0], [x1, y1, z1]])
            else:
                rectss[z0].append(Polygon([[x0, y0], [x1, y0], [x1, y1], [x0, y1]]))
            max_layer = max(max_layer, z0)

    if cur_busname is not None:
        add_objs(xyzss, liness, rectss, k, cur_busname, cur_bitname, v[1], v[2], v[3])

for z in range(1, max_layer+1):
    ax.plot([mnx, mxx, mxx, mnx, mnx], [mny, mny, mxy, mxy, mny], [z] * 5, color='gray', alpha=0.4, linewidth=5)

total_box_cnt = 2 + len(bus_obj_list)
ncols = (total_box_cnt + nrows - 1) // nrows
button_fig = plt.figure(2, figsize=(ncols, 10), dpi=108)
button_fig.canvas.mpl_connect('close_event', handle_close)
box_cnt = 0

def get_axes_box():
    global box_cnt
    h = 1 / nrows
    w = 1 / ncols
    nr = box_cnt % nrows
    nc = box_cnt // nrows
    box_cnt += 1
    return [w * nc, h * (nrows-1-nr), w, h]

all_objs_cnt = [cnt for obj, cnt in all_objs]

# "types of objects" button
types_axes = plt.axes(get_axes_box())
types_labels = []
types_actives = []
for k, v in vis.items():
    if v[0]:
        types_labels.append(k)
        types_actives.append(True)

types_check = CheckButtons(types_axes, types_labels, types_actives)
for label in types_check.labels:
    label.set_fontsize(10)
for i, line in enumerate(types_check.lines):
    line[0].set_alpha(0.6)
    line[1].set_alpha(0.6)

def type_func(label):
    assert label in obj_list
    for obj, i in obj_list[label]:
        stat = types_check.get_status()[types_labels.index(label)]
        all_objs_cnt[i] += (1 if stat else -1)
        obj.set_visible(all_objs_cnt[i] == all_objs[i][1])
    fig.canvas.draw_idle()

types_check.on_clicked(type_func)

# "layer" button
layers_axes = plt.axes(get_axes_box())
layers_labels = ['layer' + str(i) for i in range(1, max_layer + 1)]
layers_actives = [True for i in range(1, max_layer + 1)]
layers_check = CheckButtons(layers_axes, layers_labels, layers_actives)
for i, label in enumerate(layers_check.labels):
    label.set_fontsize(11)
    label.set_color(layer_colors[i+1])
for i, rect in enumerate(layers_check.rectangles):
    rect.set_color(layer_colors[i+1])
for i, line in enumerate(layers_check.lines):
    line[0].set_alpha(0.6)
    line[1].set_alpha(0.6)

def layer_func(label):
    layer_idx = int(label[5:])
    for obj, i in layer_obj_list[layer_idx]:
        stat = layers_check.get_status()[layer_idx - 1]
        all_objs_cnt[i] += (1 if stat else -1)
        obj.set_visible(all_objs_cnt[i] == 3)
    fig.canvas.draw_idle()

layers_check.on_clicked(layer_func)

# "bus" button
buses_axes, buses_checks, buses_actives, buses_labels, buses_funcs = [], [], [], [], []
for i, bus_label in enumerate(sorted(list(bus_names), key=lambda y:re.sub('\d+',lambda m:chr(int(m.group())),y))):
    buses_axes.append(plt.axes(get_axes_box()))
    buses_actives.append([True for i in range(len(bus_obj_list[bus_label])+1)])
    buses_labels.append([bus_label] + [label for label in bus_obj_list[bus_label].keys()])
    buses_checks.append(CheckButtons(buses_axes[-1], buses_labels[-1], buses_actives[-1]))
    buses_checks[-1].drawon = False
    buses_checks[-1].labels[0].set_fontsize(11)
    for label in buses_checks[-1].labels[1:]:
        label.set_fontsize(9)
    for line in buses_checks[-1].lines:
        line[0].set_alpha(0.6)
        line[1].set_alpha(0.6)

    def bus_func(label, bus_label=bus_label, i=i):
        buses_checks[i].eventson = False
        stats = buses_checks[i].get_status()
        if label == bus_label:
            for j in range(1, len(stats)):
                if stats[j] != stats[0]:
                    buses_checks[i].lines[j][0].set_visible(stats[0])
                    buses_checks[i].lines[j][1].set_visible(stats[0])
                    for obj, k in bus_obj_list[bus_label][buses_labels[i][j]]:
                        all_objs_cnt[k] += (1 if stats[0] else -1)
                        obj.set_visible(all_objs_cnt[k] == all_objs[k][1])
        else:
            j = buses_labels[i].index(label)
            if not stats[j] and stats[0]:
                buses_checks[i].lines[0][0].set_visible(False)
                buses_checks[i].lines[0][1].set_visible(False)
            elif stats[j] and all(stats[1:]):
                buses_checks[i].lines[0][0].set_visible(True)
                buses_checks[i].lines[0][1].set_visible(True)
            for obj, k in bus_obj_list[bus_label][label]:
                all_objs_cnt[k] += (1 if stats[j] else -1)
                obj.set_visible(all_objs_cnt[k] == all_objs[k][1])

        button_fig.canvas.draw_idle()
        fig.canvas.draw_idle()
        buses_checks[i].eventson = True

    buses_funcs.append(bus_func)
    buses_checks[-1].on_clicked(buses_funcs[-1])

plt.show()
