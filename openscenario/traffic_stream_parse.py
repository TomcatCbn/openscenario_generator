import json
from os.path import dirname

from .dto.lane import frameWithLanesFromJson
from .dto.records import frameWithRecordsFromJson
from .opendrive.generate_open_drive import generate_xodr
from .openscenario.generate_open_scenario import generate_xosc
from .simulator.esmini import recordGif

FILE_RECORDS = 'data/records_1618836369.6746867.json'
FILE_LANES = 'data/lane_1618836369.6746867.json'

frame_count = 0


def handle(need_gif=False):
    dir = dirname(__file__)
    print('path = %s' % (dir))

    file_lanes = '%s/%s' % (str(dir), FILE_LANES)
    # 读取所有帧的lanes信息
    with open(file_lanes, 'r') as f:
        lanes_dic = json.load(f)

    frameWithLanes = frameWithLanesFromJson(lanes_dic)

    frame_count = len(frameWithLanes.frames)

    xodrFileName = generate_xodr(frameWithLanes)

    # 读取所有帧的移动物体信息
    file_records = '%s/%s' % (str(dir), FILE_RECORDS)
    with open(file_records, 'r') as f:
        records_dic = json.load(f)

    frameWithRecords = frameWithRecordsFromJson(records_dic)
    # print(len(frameWithRecords.records))

    xoscFileName, total_time = generate_xosc(frameWithRecords.records, xodrFileName)

    # 仿真运行，移到对应esmini环境下
    if need_gif:
        gif_file_path = recordGif(xodrFileName, xoscFileName, int(total_time))
    else:
        gif_file_path = ''
    return xodrFileName, xoscFileName, gif_file_path
