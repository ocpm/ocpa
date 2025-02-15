import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.transforms import Bbox
import matplotlib.patches as patches
import matplotlib.cm as cm
from ocpa.algo.conformance.alignments.alignment import Move, Alignment, DefinedModelMove, SynchronousMove, LogMove
from typing import List, Set, Dict, Tuple, Optional
import re
from functools import reduce

MOVE_WIDTH = 6
ACTIVITY_HIGHT = 2
OBJECT_HEIGHT = 1
BUFFER_HEIGHT = 0.5
BUFFER_WIDTH = 0.5
SPACE_BETWEEN_COLUMNS = 1
TEXT_BUFFER_TOP = 0.1
TEXT_BUFFER_LEFT = 0.3
TEXT_BUFFER_RIGHT = 0.1

SYNC_LINESTYLE = 'solid'
MODEL_MOVE_LINESTYLE = (0, (1,1))
LOG_MOVE_LINESTYLE = (0,(5,1))
DEFAULT_LINESTYLE = "solid"

# SYNC_COLOR = '#000000'
# MODEL_MOVE_COLOR = "orange"
# LOG_MOVE_COLOR = "red"
# DEFAULT_COLOR = "white"



def use_fontsize_that_fits(text, width, height, fig=None, ax=None):
    '''Automatically decrease the fontsize until it fits the width and height. The axis need to be set already.

    Args:
        text (matplotlib.text.Text)
        width (float): allowed width in data coordinates
        height (float): allowed height in data coordinates
    '''
    fig = fig or plt.gcf()
    ax = ax or plt.gca()

    # bounding box of text in figure coordinates and transform to data coordinates
    ren = fig.canvas.get_renderer()
    bbox_text = text.get_window_extent(renderer=ren)
    bbox_text = Bbox(ax.transData.inverted().transform(bbox_text))

    # check if already in box
    fits_width = bbox_text.width < width if width else True
    fits_height = bbox_text.height < height if height else True
    # if it does not fit decrease further
    if not all((fits_width, fits_height)):
        if text.get_fontsize() > 1:
            text.set_fontsize(text.get_fontsize()-1)
            use_fontsize_that_fits(text, width, height, fig, ax)

def calculate_object_colors(alignment: Alignment):
    object_colors = dict()

    if alignment.object_types == None:
        # print("No OT")
        pass

    else:
        # print("Has OT")
        # print(alignment.object_types)
        object_by_type = dict()
        for type, object in alignment.object_types:
            object_by_type.setdefault(type, [])
            object_by_type[type].append(object)
        color_map_names = ["Greens", "Blues", "Purples", "Reds", "Oranges"]
        for count, type in enumerate(object_by_type.keys()):
            cmap = cm.get_cmap(color_map_names[count % len(color_map_names)])
            total_obj_in_type = len(object_by_type[type])
            for count, obj in enumerate(object_by_type[type]):
                object_colors[obj] = cmap(1 - (((count+1) / total_obj_in_type) * 0.75 + 0.125))
                # print(f"Obj: {obj} Color: {object_colors[obj]}")

    return object_colors

def id_of_earliest_obj(move: Move, objects):
    earliest_id = None
    for obj in move.objects:
        this_id = objects.index(obj)
        if earliest_id == None or this_id < earliest_id:
            earliest_id = this_id
    return earliest_id

def draw_line(start, end, fig, ax):
    verts = [start, end]

    codes = [Path.MOVETO, Path.LINETO]

    path = Path(verts, codes)
    patch = patches.PathPatch(path, lw=2)
    ax.add_patch(patch)


def draw_move(move: Move, object_colors, start_x: int, start_y: int, linestyle: str, abbreviations: Dict[str, str], fig, ax, renderer) \
        -> Tuple[int, Dict[Move, Tuple[int, int]], Dict[Move, Tuple[int, int]]]:
    '''
    Visualizes a Move to a given mathplootlib plot.
    :param move: Move that should be visualized.
    :param object_colors: Dictonary with objects as keys and colors as values.
    :param start_x: Xcoordinate of upper left corner of the box that will represent the move.
    :param start_y: Y coordinate of upper left corner of the box that will represent the move.
    :return: Width this column used.
    '''

    # draw background
    background_box_count = len(move.objects)
    drawn_objects = 0
    for obj in object_colors.keys():
        if obj in move.objects:
            bg_act_verts = [
                (start_x + (MOVE_WIDTH / background_box_count) * drawn_objects, start_y),  # left, top
                (start_x + (MOVE_WIDTH / background_box_count) * drawn_objects + MOVE_WIDTH / background_box_count, start_y),  # right, top
                (start_x + (MOVE_WIDTH / background_box_count) * drawn_objects + MOVE_WIDTH / background_box_count, start_y - ACTIVITY_HIGHT * 2 - OBJECT_HEIGHT * 2),  # right, top
                (start_x + (MOVE_WIDTH / background_box_count) * drawn_objects, start_y - ACTIVITY_HIGHT * 2 - OBJECT_HEIGHT * 2),  # left, bottom
                (start_x + (MOVE_WIDTH / background_box_count) * drawn_objects, start_y),  # left, top
            ]

            bg_act_codes = [
                Path.MOVETO,
                Path.LINETO,
                Path.LINETO,
                Path.LINETO,
                Path.LINETO,
            ]

            log_activity_box_path = Path(bg_act_verts, bg_act_codes)
            log_activity_box_patch = patches.PathPatch(log_activity_box_path, facecolor=object_colors[obj], lw=0)
            ax.add_patch(log_activity_box_patch)
            drawn_objects += 1


    # draw log activity box
    log_act_verts = [
        (start_x, start_y),  # left, top
        (start_x + MOVE_WIDTH, start_y),  # right, top
        (start_x + MOVE_WIDTH, start_y - ACTIVITY_HIGHT),  # right, top
        (start_x, start_y - ACTIVITY_HIGHT),  # left, bottom
        (start_x, start_y),  # left, top
    ]

    log_act_codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
    ]

    log_activity_box_path = Path(log_act_verts, log_act_codes)
    log_activity_box_patch = patches.PathPatch(log_activity_box_path, facecolor='none', lw=2, linestyle=linestyle)
    ax.add_patch(log_activity_box_patch)

    # draw log object box
    log_ob_y = start_y - ACTIVITY_HIGHT

    log_obj_verts = [
        (start_x, log_ob_y),  # left, top
        (start_x + MOVE_WIDTH, log_ob_y),  # right, top
        (start_x + MOVE_WIDTH, log_ob_y - OBJECT_HEIGHT),  # right, top
        (start_x, log_ob_y - OBJECT_HEIGHT),  # left, bottom
        (start_x, log_ob_y),  # left, top
    ]

    log_obj_codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
    ]

    log_obj_box_path = Path(log_obj_verts, log_obj_codes)
    log_obj_box_patch = patches.PathPatch(log_obj_box_path, facecolor='none', lw=2, linestyle=linestyle)
    ax.add_patch(log_obj_box_patch)

    # draw model activity box
    model_start_y = start_y - ACTIVITY_HIGHT - OBJECT_HEIGHT
    model_act_verts = [
        (start_x, model_start_y),  # left, top
        (start_x + MOVE_WIDTH, model_start_y),  # right, top
        (start_x + MOVE_WIDTH, model_start_y - ACTIVITY_HIGHT),  # right, top
        (start_x, model_start_y - ACTIVITY_HIGHT),  # left, bottom
        (start_x, model_start_y),  # left, top
    ]

    model_act_codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
    ]

    model_activity_box_path = Path(model_act_verts, model_act_codes)
    model_activity_box_patch = patches.PathPatch(model_activity_box_path, facecolor='none', lw=2, linestyle=linestyle)
    ax.add_patch(model_activity_box_patch)

    # draw model object box
    model_ob_y = start_y - ACTIVITY_HIGHT - OBJECT_HEIGHT - ACTIVITY_HIGHT

    model_obj_verts = [
        (start_x, model_ob_y),  # left, top
        (start_x + MOVE_WIDTH, model_ob_y),  # right, top
        (start_x + MOVE_WIDTH, model_ob_y - OBJECT_HEIGHT),  # right, top
        (start_x, model_ob_y - OBJECT_HEIGHT),  # left, bottom
        (start_x, model_ob_y),  # left, top
    ]

    model_obj_codes = [
        Path.MOVETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
        Path.LINETO,
    ]

    model_obj_box_path = Path(model_obj_verts, model_obj_codes)
    model_obj_box_patch = patches.PathPatch(model_obj_box_path, facecolor='none', lw=2, linestyle=linestyle)
    ax.add_patch(model_obj_box_patch)

    # log activity text
    log_act = move.log_move if move.log_move else ">>"
    if log_act in abbreviations.keys():
        log_act = abbreviations[log_act]
    log_act_text = ax.text(start_x + TEXT_BUFFER_LEFT,
                           start_y - (0.5 * ACTIVITY_HIGHT),
                           log_act,
                           va='center', ha='left',
                           fontsize=12)
    use_fontsize_that_fits(log_act_text, MOVE_WIDTH - (2 * TEXT_BUFFER_LEFT), ACTIVITY_HIGHT, fig=fig, ax=ax)

    # model activity text
    model_act = move.model_move if move.model_move else ">>"
    if model_act in abbreviations.keys():
        model_act = abbreviations[model_act]
    model_act_text = ax.text(start_x + TEXT_BUFFER_LEFT,
                           start_y - ACTIVITY_HIGHT - OBJECT_HEIGHT - (0.5 * ACTIVITY_HIGHT),
                           model_act,
                           va='center', ha='left',
                           fontsize=12)
    use_fontsize_that_fits(model_act_text, MOVE_WIDTH - (2 * TEXT_BUFFER_LEFT), ACTIVITY_HIGHT, fig=fig, ax=ax)

    # log objects text
    log_obj = ""
    for obj in move.objects:
        obj_str = obj
        if obj_str in abbreviations.keys():
            log_obj += obj_str + " "
            continue
        numb_obj_str = re.findall(r'\d+', obj_str)
        no_number_obj_str = ''.join([i for i in obj_str if not i.isdigit()])
        if no_number_obj_str in abbreviations.keys():
            number = reduce(lambda a, b: a+b, numb_obj_str)
            number = number[0]
            log_obj += abbreviations[no_number_obj_str] + number + " "
            continue
        log_obj += obj_str + " "

    log_obj_text = ax.text(start_x + TEXT_BUFFER_LEFT,
                             start_y - ACTIVITY_HIGHT - (0.5 * OBJECT_HEIGHT),
                             log_obj,
                             va='center', ha='left',
                             fontsize=12)
    use_fontsize_that_fits(log_obj_text, MOVE_WIDTH - (2 * TEXT_BUFFER_LEFT), OBJECT_HEIGHT, fig=fig, ax=ax)

    # model objects text
    # use same text as log

    model_obj_text = ax.text(start_x + TEXT_BUFFER_LEFT,
                           start_y - ACTIVITY_HIGHT - ACTIVITY_HIGHT - OBJECT_HEIGHT - (0.5 * OBJECT_HEIGHT),
                           log_obj,
                           va='center', ha='left',
                           fontsize=12)
    use_fontsize_that_fits(model_obj_text, MOVE_WIDTH - (2 * TEXT_BUFFER_LEFT), ACTIVITY_HIGHT, fig=fig, ax=ax)

    return (MOVE_WIDTH, (start_x, model_start_y), (start_x + MOVE_WIDTH, model_start_y))


def alignment_viz(alignment: Alignment, abbreviations=dict()):
    # get all objects
    objects = []

    move: Move
    for move in alignment.moves:
        objects += move.objects
    # remove duplicates
    objects = set(objects)
    objects = list(objects)

    # map objects to colors
    object_colors = calculate_object_colors(alignment)


    # get minimal set of transition to have equivalent transitive hull
    connections = set()
    for object in objects:
        last_move_with_object = None
        for move in alignment.moves:
            if object in move.objects:
                if last_move_with_object != None:
                    connections.add((last_move_with_object, move))
                last_move_with_object = move

    # get start moves that don't have ingoing arc
    not_selected_moves = alignment.moves[:]
    selected_moves = []
    columns = []
    first_column = []
    for move in not_selected_moves:
        to_add = []
        has_ingoing = False
        for connection in connections:
            if connection[1] == move:
                has_ingoing = True
                break
        if not has_ingoing:
            to_add.append(move)
            not_selected_moves.remove(move)
            first_column.append(move)
        selected_moves += to_add
    columns.append(first_column)

    # always get moves that only have ingoing arcs from currently already selected notes. They then form new front
    while not_selected_moves:
        to_add = []
        to_remove = []
        this_column = []
        for move in not_selected_moves:
            all_ingoing_selected = True
            for connection in connections:
                if connection[1] == move:
                    if connection[0] not in selected_moves:
                        all_ingoing_selected = False
                        break

            if all_ingoing_selected:
                to_add.append(move)
                to_remove.append(move)
                this_column.append(move)
        selected_moves += to_add
        for move in to_remove:
            not_selected_moves.remove(move)
        columns.append(this_column)

    max_column_count = max([len(column) for column in columns])
    total_y_axis_height = BUFFER_HEIGHT + max_column_count * (BUFFER_HEIGHT + 2 * (ACTIVITY_HIGHT + OBJECT_HEIGHT))
    total_x_axis_width = 2 * BUFFER_WIDTH + (len(columns) - 1) * SPACE_BETWEEN_COLUMNS + len(columns) * MOVE_WIDTH
    # draw each column
    fig, ax = plt.subplots()
    renderer = fig.canvas.get_renderer()
    ax.set_xlim(0, total_x_axis_width)
    ax.set_ylim(0, total_y_axis_height)

    # initialize dictionary to save in and outgoing point for moves
    ingoing_points = dict()
    outgoing_points = dict()

    start_x_axis = BUFFER_WIDTH

    #sort columns
    for column in columns:
        column.sort(key=lambda mv: id_of_earliest_obj(mv, objects))


    for column in columns:
        start_y_axis = 0.5 * total_y_axis_height + 0.5 * (BUFFER_HEIGHT + len(column) * (BUFFER_HEIGHT + 2 * (ACTIVITY_HIGHT + OBJECT_HEIGHT))) - BUFFER_HEIGHT
        current_move_start_x = start_x_axis
        max_used_width = 0
        for move in column:
            linestyle_of_move = DEFAULT_LINESTYLE
            if isinstance(move, DefinedModelMove):
                linestyle_of_move = MODEL_MOVE_LINESTYLE
            if isinstance(move, SynchronousMove):
                linestyle_of_move = SYNC_LINESTYLE
            if isinstance(move, LogMove):
                linestyle_of_move = LOG_MOVE_LINESTYLE
            used_width, ingoing_point, outgoing_point = draw_move(move, object_colors, current_move_start_x, start_y_axis,
                                                                  linestyle_of_move, abbreviations, fig, ax, renderer)
            if used_width > max_used_width:
                max_used_width = used_width
            ingoing_points[move] = ingoing_point
            outgoing_points[move] = outgoing_point
            start_y_axis = start_y_axis - BUFFER_HEIGHT - (2 * (ACTIVITY_HIGHT + OBJECT_HEIGHT))
        start_x_axis = start_x_axis + max_used_width + SPACE_BETWEEN_COLUMNS

    # draw lines
    for connection in connections:
        draw_line(outgoing_points[connection[0]], ingoing_points[connection[1]], fig, ax)

    ax.set_title(f"Alignment has cost: {alignment.get_cost()}")

    sync_patch = mpatches.Patch(linestyle=SYNC_LINESTYLE, label='Synchronous Move', linewidth=2, facecolor='none', edgecolor="black")
    model_patch = mpatches.Patch(linestyle=MODEL_MOVE_LINESTYLE, label='Model Move', linewidth=2, facecolor='none', edgecolor="black")
    label_patch = mpatches.Patch(linestyle=LOG_MOVE_LINESTYLE, label='Log Move', linewidth=2, facecolor='none', edgecolor="black")
    ax.legend(handles=[sync_patch, model_patch, label_patch])

    ax.set_xlim(0, start_x_axis - SPACE_BETWEEN_COLUMNS + BUFFER_WIDTH)
    ax.set_ylim(0, total_y_axis_height)

    # hide x-axis
    ax.get_xaxis().set_visible(False)

    # hide y-axis
    ax.get_yaxis().set_visible(False)

    #plt.show()

    return plt
