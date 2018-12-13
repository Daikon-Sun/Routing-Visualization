#!/usr/bin/python3
import sys, random, re
from functools import partial
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.dockarea import *
import matplotlib

pg.setConfigOptions(antialias=True)
app = QtGui.QApplication([])
win = QtGui.QMainWindow()
area = DockArea()
win.setCentralWidget(area)
vis_dock = Dock("Visualization", size=(100,100))
button_dock = Dock("Buttons", size=(1,1))
scroll = QtGui.QScrollArea()
button_group = QtGui.QGroupBox()
vbox = QtGui.QVBoxLayout()
button_group.setLayout(vbox)
area.addDock(button_dock)
area.addDock(vis_dock, 'left', button_dock)

if len(sys.argv) < 2:
    print('usage : python3 {} test_case_name [bus_name1 bus_name2 ...]'.format(__file__))
    print('if no bus_name is typed, all buses will be considered')
    exit()

vis_all = len(sys.argv) == 2
filename = sys.argv[1]
max_total_layer = 6
nrows = 2

layer_colors = list(map(matplotlib.colors.to_rgb, ['blue', 'red', 'green', 'orange', 'purple', 'cyan']))
layer_colors = list(map(lambda x:(int(x[1][0]*255),int(x[1][1]*255),int(x[1][2]*255),180), enumerate(layer_colors)))

#                (On/Off, linewidth, symbol)
# symbol : {'o', 't', 't1', 't2', 't3', 's', 'p', 'h', 'star', '+', 'd'}
vis = {
    'track':     (True,  1, None),
    'obs':       (True,  6, None),
    'bus':       (True,  6, None)
}

bus_names = set([sys.argv[i] for i in range(2, len(sys.argv))])
bus_names.add('__ALL__')

plt = pg.PlotWidget(title=sys.argv[1])
vis_dock.addWidget(plt)

layer_obj_list = [[] for i in range(max_total_layer)]
max_layer = 0
obj_list = {}
bus_obj_list = dict([[bus_name, dict()] for bus_name in bus_names])
all_objs, all_objs_cnt, all_infoss = [], [], []

def add_obj(obj, z, obj_type, busname, bitname):
    obj.setZValue(z)
    plt.addItem(obj)
    layer_obj_list[z].append((obj, len(all_objs)))
    obj_list[obj_type].append((obj, len(all_objs)))
    if bitname not in bus_obj_list[busname]:
        bus_obj_list[busname][bitname] = []
    bus_obj_list[busname][bitname].append((obj, len(all_objs)))
    all_objs.append((obj, 3))
    all_objs_cnt.append(3)

def print_info(event):
    x = event.lastPos().x()
    y = event.lastPos().y()
    clicked_infos = []
    for i in range(len(all_infoss)):
        if all_objs_cnt[i] != all_objs[i][1]:
            continue
        infos, tz, busname, bitname = all_infoss[i]
        for info in infos:
            if info[0] <= x <= info[0]+info[2] and info[1] <= y <= info[1]+info[3]:
                name = "{}, {}".format(busname, bitname)
                xyz = "({:d}, {:d}, {:d}), ({:d}, {:d}, {:d})".format(info[0], info[1], tz, info[0]+info[2], info[1]+info[3], tz)
                wh = "width = {}, height = {}".format(info[2], info[3])
                clicked_infos.append("\n".join(["-"*30, xyz, wh, name]))
    msg = QtGui.QMessageBox(
        QtGui.QMessageBox.Information,
        "Informations",
        "clicked on {}, {}\n".format(int(x), int(y)) + "\n".join(clicked_infos)
    )
    msg.exec_()

def lines_to_rects(ls):
    rtn = []
    for i in range(0, len(ls[0]), 2):
        rtn.append((ls[0][i], ls[1][i], ls[0][i+1]-ls[0][i], ls[1][i+1]-ls[1][i]))
    return rtn

def add_objs(xyss, liness, rectss, obj_type, busname, bitname, pens, brushes, linewidth, symbol):
    for z, (xs, ys) in enumerate(xyss):
        if len(xs) > 0:
            scatter = pg.ScatterPlotItem(size=linewidth, pen=None, symbol=symbol, symbolBrush=brushes[z-1])
            scatter.addPoints(xs, ys)
            add_obj(scatter, z, k, busname, bitname)
    for z, lines in enumerate(liness):
        if len(lines[0]) > 0:
            connect = np.ones(len(lines[0]), dtype=np.ubyte)
            connect[1::2] = 0
            line = pg.arrayToQPath(np.array(lines[0]), np.array(lines[1]), connect)
            line = QtGui.QGraphicsPathItem(line)
            line.setPen(pens[z-1])
            add_obj(line, z, k, busname, bitname)
            all_infoss.append((lines_to_rects(lines), z, busname, bitname))

    for z, rects in enumerate(rectss):
        if len(rects) > 0:
            obj = QtGui.QGraphicsItemGroup()
            for i, rect in enumerate(rects):
                rect = QtGui.QGraphicsRectItem(*rect)
                rect.setPen(pens[z-1])
                rect.setBrush(brushes[z-1])
                obj.addToGroup(rect)
            obj.mouseDoubleClickEvent = print_info
            add_obj(obj, z, k, busname, bitname)
            all_infoss.append((rects, z, busname, bitname))

for k, v in vis.items():
    if not v[0]:
        continue
    print(k)
    pens = [pg.mkPen(color, width=v[1]) for color in layer_colors]
    brushes = [pg.mkBrush(color) for color in layer_colors]
    obj_list[k] = []
    cur_busname = None
    for line in open(filename + '.' + k, 'r'):
        content = line.split()
        if len(content) <= 2:
            if content[0] != '(' and content[0] != ')':
                if cur_busname is not None:
                    add_objs(xyss, liness, rectss, k, cur_busname, cur_bitname, pens, brushes, v[1], v[2])
                xyss = [[[], []] for i in range(max_total_layer)]
                liness = [[[], []] for i in range(max_total_layer)]
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
                x0, y0, z0, x1, y1, z1 = map(int, content)
            else:
                x0, y0, z0 = map(int, content)
                x1, y1, z1 = x0, y0, z0

            if len(content) == 3 or (x0 == x1 and y0 == y1):
                xyss[z0][0].append(x0)
                xyss[z0][1].append(y0)
                if len(content) == 6:
                    xyss[z1][0].append(x0)
                    xyss[z1][1].append(y0)
            elif x0 == x1 or y0 == y1:
                liness[z0][0].extend([x0, x1])
                liness[z0][1].extend([y0, y1])
            else:
                rectss[z0].append((x0, y0, x1-x0, y1-y0))
            max_layer = max(max_layer, z0)

    if cur_busname is not None:
        add_objs(xyss, liness, rectss, k, cur_busname, cur_bitname, pens, brushes, v[1], v[2])

print('done')

def update_st(st, objs):
    for obj, i in objs:
        if st:
            all_objs_cnt[i] += 1
            if all_objs_cnt[i] == all_objs[i][1]:
                obj.show()
        else:
            all_objs_cnt[i] -= 1
            if all_objs_cnt[i] != all_objs[i][1]:
                obj.hide()

# types
type_actions = []
type_menu = QtGui.QMenu()
for i, (k, v) in enumerate(vis.items()):

    if v[0]:
        if k == 'bus':
            bus_idx = len(type_actions)
        type_actions.append(type_menu.addAction(k))
        type_actions[-1].setCheckable(True)
        type_actions[-1].setChecked(True)

        if k != 'bus':
            def type_func(st, label):
                update_st(st, obj_list[label])

            type_actions[-1].toggled.connect(partial(type_func, label=k))

main_type_button = QtGui.QPushButton("Types")
main_type_button.setMenu(type_menu)
vbox.addWidget(main_type_button)

# layers
layer_menu = QtGui.QMenu()
for i in range(1, max_layer + 1):
        action = layer_menu.addAction('L'+str(i))
        action.setCheckable(True)
        action.setChecked(True)

        def layer_func(st, idx):
            update_st(st, layer_obj_list[idx])

        action.toggled.connect(partial(layer_func, idx=i))

main_layer_button = QtGui.QPushButton("Layers")
main_layer_button.setMenu(layer_menu)
vbox.addWidget(main_layer_button)

def sort_with_num(y):
    return re.sub('\d+', lambda m:m.group().zfill(9), y)

# bus
bus_names = list(sorted(list(set(bus_names)-set(['__ALL__'])), key=sort_with_num))
bus_labelss, bus_actionss = [], []
for i, busname in enumerate(bus_names):
    bus_button = QtGui.QPushButton(busname)
    bus_menu = QtGui.QMenu()
    font = bus_menu.font()
    font.setPointSize(9)
    bus_menu.setFont(font)
    bus_button.setMenu(bus_menu)
    vbox.addWidget(bus_button)
    bus_labelss.append([busname] + list(sorted([label for label in bus_obj_list[busname].keys()], key=sort_with_num)))
    actions = []
    for name in bus_labelss[-1]:
        actions.append(bus_menu.addAction(name))
        actions[-1].setCheckable(True)
        actions[-1].setChecked(True)
    bus_actionss.append(actions)

def reset_action(action, st):
    action.blockSignals(True)
    action.setChecked(st)
    action.blockSignals(False)

for i, (bus_labels, actions) in enumerate(zip(bus_labelss, bus_actionss)):
    for j, (bus_label, action) in enumerate(zip(bus_labels, actions)):

        def bus_func(st, i, j):
            bit_sts = [action.isChecked() for action in bus_actionss[i]]
            bus_sts = [actions[0].isChecked() for actions in bus_actionss]
            if j == 0:
                if not st and type_actions[bus_idx].isChecked():
                    reset_action(type_actions[bus_idx], False)
                elif st and all(bus_sts):
                    reset_action(type_actions[bus_idx], True)
                for k in range(1, len(bit_sts)):
                    if bit_sts[k] != st:
                        bit_sts[k] = st
                        update_st(st, bus_obj_list[bus_labelss[i][0]][bus_labelss[i][k]])

            else:
                if not st and bit_sts[0]:
                    bit_sts[0] = False
                    if type_actions[bus_idx].isChecked():
                        reset_action(type_actions[bus_idx], False)

                elif st and all(bit_sts[1:]):
                    bit_sts[0] = True
                    bus_sts[i] = True
                    if all(bus_sts):
                        reset_action(type_actions[bus_idx], True)
                update_st(st, bus_obj_list[bus_labelss[i][0]][bus_labelss[i][j]])
            for k, action in enumerate(bus_actionss[i]):
                reset_action(action, bit_sts[k])

        action.toggled.connect(partial(bus_func, i=i, j=j))

if vis['bus'][0]:
    action = type_actions[bus_idx]

    def bus_type_func(st):
        for bus_labels, actions in zip(bus_labelss, bus_actionss):
            if actions[0].isChecked() != st:
                reset_action(actions[0], st)
            for bus_label, action in zip(bus_labels[1:], actions[1:]):
                if action.isChecked() != st:
                    update_st(st, bus_obj_list[bus_labels[0]][bus_label])
                    reset_action(action, st)

    type_actions[bus_idx].toggled.connect(bus_type_func)

scroll.setWidget(button_group)
button_dock.addWidget(scroll)

win.show()
assert (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION')
QtGui.QApplication.instance().exec_()
