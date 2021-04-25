import json
import os

from .dto.lane import frameWithLanesFromJson
from .dto.records import frameWithRecordsFromJson
from .opendrive.generate_open_drive import generate_xodr
from .openscenario.generate_open_scenario import generate_xosc
from os.path import dirname

FILE_RECORDS = 'data/records_1618836369.6746867.json'
FILE_LANES = 'data/lane_1618836369.6746867.json'

ESMINI_ENV_PATH = '/Users/uvaw4pv/ma/asam/OpenScenario/esmini-demo/resources/samples/'


def __exec_cmd(s):
    print('exec cmd ' + s)
    os.system(s)


frame_count = 0


def handle():
    dir = dirname(__file__)
    print('path = %s'%(dir))

    file_lanes = '%s/%s'%(str(dir), FILE_LANES)
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

    xoscFileName = generate_xosc(frameWithRecords.records, xodrFileName)

    # 仿真运行，移到对应esmini环境下

    __exec_cmd('cp %s %s' % (xodrFileName, ESMINI_ENV_PATH))
    __exec_cmd('cp %s %s' % (xoscFileName, ESMINI_ENV_PATH))

    esmini_cmd = 'esmini --osc %s%s --window 60 60 1024 720 --camera_mode top' % (ESMINI_ENV_PATH, xoscFileName)
    __exec_cmd(esmini_cmd)
    return xodrFileName, xoscFileName
