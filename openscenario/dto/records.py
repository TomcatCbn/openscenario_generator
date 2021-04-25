import math
class FramesWrapRecords:
    def __init__(self, records):
        self.records = records


class Record:
    def __init__(self, timestamp, ego, objects):
        self.timestamp = timestamp
        self.ego = ego
        self.objects = objects


class Ego:
    def __init__(self, w, l, h, speed, lane_id):
        self.w = w
        self.l = l
        self.h = h
        self.speed = speed
        self.land_id = lane_id

    def __str__(self):
        return '{speed=%.0f, lane_id=%s}' % (self.speed, self.land_id)


class Objects:
    def __init__(self, object):
        self.object = object


class Object:
    def __init__(self, cars):
        self.cars = cars
    
    def __str__(self):
        s=[]
        for car in self.cars:
            s.append(str(car))
        return 'cars size=%d, {%s}'%(len(self.cars), ";".join(s))


class Car:
    def __init__(self, id, x, y, z, w, l, h, lane_id, timestamp):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.w = w
        self.l = l
        self.h = h
        self.lane_id = lane_id
        self.timestamp=timestamp

    def __str__(self):
        return '{id=%s,lane_id=%s}' % (self.id, self.lane_id)


def frameWithRecordsFromJson(dic):
    frames = []
    if isinstance(dic, list):
        print('len of frames in records = '+str(len(dic)))
        for frame in dic:
            record = recordsFromJson(frame)
            if record:
                frames.append(record)

        return FramesWrapRecords(frames)

# 从dict获取records，并带上时间戳


def recordsFromJson(dic):
    # print('lanesFromJson:'+str(dic))
    if dic['timestamp']:
        ego = egoFromJson(dic['ego'])

        obj = objectFromJson(dic['objects'], dic['timestamp'])
        objects = Objects(obj)

        return Record(dic['timestamp'], ego, objects)


def egoFromJson(dic):
    return Ego(dic['w'], dic['l'], dic['h'], dic['speed'], dic['lane_id'])

# 从dict获取单个lane类


def objectFromJson(dic, timestamp):
    cars_dic = dic['cars']
    if isinstance(cars_dic, list):
        cars = []
        for car in cars_dic:
            cars.append(Car(car['id'], car['x'], car['y'], car['z'],
                        car['w'], car['l'], car['h'], car['lane_id'],timestamp))
        return Object(cars)

def findLaneChanged(objList):
    if len(objList) > 0:
        temp = objList[0]
        for car in objList:
            if not car.lane_id == temp.lane_id:
                print('find car(%d) lane changed, from lane(%s) to lane(%s)'%(car.id,temp.lane_id,car.lane_id))
            temp = car

def findCarSpeed(values):
    if len(values) > 1:
        lastState = values[0]
        for i in range(1,len(values)):
            temp = values[i]
            velo = (math.sqrt(pow(temp.x-lastState.x,2)+pow(temp.y-lastState.y,2)))/(temp.timestamp-lastState.timestamp)
            print('carid=%d, speed=%f'%(temp.id,velo*3.6))
