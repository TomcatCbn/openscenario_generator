from scenariogeneration import xodr
from ..dto.lane import FramesWrapLanes, getRoadIdAndLaneId

import os
import math

XODR_FILE_PATH = '/Users/uvaw4pv/ma/asam/OpenScenario/scenariogeneration-main/examples/trafficstream/generate_open_drive.xodr'


def generate_xodr(framesWrapLanes):
    if isinstance(framesWrapLanes, FramesWrapLanes):
        print('begin to generate xodr ...')
        frames_count = len(framesWrapLanes.frames)
        print('frame count = ' + str(frames_count))

        roadChangedFrameIndex = __findRoadChangedIndex(framesWrapLanes.frames)
        print('road changed frame index = %s' % (list(roadChangedFrameIndex)))

        # generate road in xodr
        roads = []

        tempIndex = 0

        for index in roadChangedFrameIndex:
            roads.append(__generate_xodr_road(
                framesWrapLanes.frames[tempIndex: index]))
            tempIndex = index

        if tempIndex < frames_count:
            roads.append(__generate_xodr_road(framesWrapLanes.frames[tempIndex: frames_count]))

        print('roads=%s' % ([x.id for x in roads]))
        # add some connections to non junction roads
        # roads[0].add_successor(xodr.ElementType.junction,1)
        if len(roads) >= 2:
            for i in range(1, len(roads)):
                roads[i - 1].add_successor(xodr.ElementType.road, roads[i].id, xodr.ContactPoint.start)
                roads[i].add_predecessor(xodr.ElementType.road, roads[i - 1].id, xodr.ContactPoint.end)

        # junction = xodr.create_junction(roads[1:],1,roads[0:1])

        # create the opendrive
        odr = xodr.OpenDrive('myroad')
        for r in roads:
            odr.add_road(r)
        odr.adjust_roads_and_lanes()

        # write the OpenDRIVE file as xodr using current script name
        odr.write_xml(os.path.basename(__file__).replace('.py', '.xodr'))

        fileName = os.path.basename(__file__).replace('.py', '.xodr')

        print('generate file name = ' + fileName)

        return fileName


def __generate_xodr_road(frames):
    if isinstance(frames, list):
        count = len(frames)
        firstFrame = frames[0]
        lastFrame = frames[count - 1]
        print('generate xodr road with frames from %s to %s' %
              (firstFrame, lastFrame))

        lane_count = len(firstFrame.lanes)
        # easy way to cacl length of road
        startPoint = firstFrame.lanes[0].way_point[0]
        endPoint = lastFrame.lanes[0].way_point[len(lastFrame.lanes[0].way_point) - 1]

        roadLength = math.sqrt(math.pow(endPoint.y - startPoint.y, 2) + math.pow(endPoint.x - startPoint.x, 2))
        roadLength = 500
        roadId, _ = getRoadIdAndLaneId(firstFrame.lanes[0].id)
        lanes_width = firstFrame.lanes[0].way_point[0].width
        # for lane in firstFrame.lanes:
        # lanes_width += lane.way_point[0].width

        print('generate xodr road length =%s, roadId=%s, left_lanes=%d, right_lanes=%s, lanes_width=%f' % (
            roadLength, roadId, 0, lane_count, lanes_width))
        return xodr.create_road(xodr.Line(roadLength),
                                id=roadId, left_lanes=6, right_lanes=lane_count, lane_width=lanes_width)


# 目前数据中的lanes可能包含多条roadid
def __findRoadChangedIndex(frames):
    count = len(frames)
    if count <= 0:
        return 0

    curFrame = frames[0]
    curRoad, curLane = getRoadIdAndLaneId(curFrame.lanes[0].id)
    changedIndex = []
    for index in range(count):
        tempFrame = frames[index]

        tempRoad, tempLane = getRoadIdAndLaneId(tempFrame.lanes[0].id)
        if not curRoad == tempRoad:
            changedIndex.append(index)
            curRoad = tempRoad
            curLane = tempLane

        curFrame = tempFrame
    return changedIndex
