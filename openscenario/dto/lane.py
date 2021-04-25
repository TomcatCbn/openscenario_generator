class FramesWrapLanes:
    def __init__(self, frames):
        self.frames = frames


class Lanes:
    def __init__(self, timestamp, lanes):
        self.timestamp = timestamp
        self.lanes = lanes

    def __str__(self):
        return '{timestamp=%s, lanes_count=%d}'%(self.timestamp,len(self.lanes))


class Lane:
    def __init__(self, id, way_point):
        self.id = id
        roadId, laneId = getRoadIdAndLaneId(id)
        self.roadId = roadId
        self.laneId = laneId
        self.way_point = way_point


class WayPointItem:
    def __init__(self, id, x, y, z, width, marking_type, marking_color, marking_width):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.width = width
        self.marking_type = marking_type
        self.marking_color = marking_color
        self.marking_width = marking_width


def frameWithLanesFromJson(dic):
    frames = []
    if isinstance(dic, list):
        print('len of frames in lanes = '+str(len(dic)))
        for frame in dic:
            lanes = lanesFromJson(frame)
            if lanes:
                frames.append(lanes)

        return FramesWrapLanes(frames)

# 从dict获取lanes，并带上时间戳


def lanesFromJson(dic):
    # print('lanesFromJson:'+str(dic))
    if dic['timestamp']:
        if dic['lanes']:
            lanes = []
            lanes_temp = dic['lanes']
            if isinstance(lanes_temp, list):
                for lane in lanes_temp:
                    # print(lane)
                    item = laneFromJson(lane)
                    if item:
                        lanes.append(item)

    return Lanes(dic['timestamp'], lanes)

# 从dict获取单个lane类


def laneFromJson(dic):
    waypoints = []
    if dic['id']:
        array = dic['way_point']
        if isinstance(array, list):
            for way_point in array:
                item = wayPointItemFromJson(way_point)
                if item:
                    waypoints.append(item)

        return Lane(dic['id'], waypoints)


# 从dict获取单个waypoint类
def wayPointItemFromJson(dic):
    # print('wayPointItemFromJson:'+str(dic))
    if dic['id']:
        return WayPointItem(dic['id'],
                            dic['x'],
                            dic['y'],
                            dic['z'],
                            dic['width'],
                            dic['marking_type'],
                            dic['marking_color'],
                            dic['marking_width'])

def getRoadIdAndLaneId(s):
    if isinstance(s, str):
        temp = s.split('_')
        return temp[0], temp[1]
    else:
        return '0', '0'
