import math
import os
from enum import Enum, auto

from scenariogeneration import xosc

from ..dto.lane import getRoadIdAndLaneId

XOSC_FILE_PATH = '/Users/uvaw4pv/ma/asam/OpenScenario/scenariogeneration-main/examples/trafficstream/generate_open_scenario.xosc'
VEHICLE_CATALOG = '/Users/uvaw4pv/ma/asam/OpenScenario/esmini-demo/resources/xosc/Catalogs/Vehicles'

carCatalog = {0: 'car_blue', 1: 'car_yellow', 2: 'car_red'}
EGO_ID = '0'


def generate_xosc(frames, xodrFileName):
    if not isinstance(frames, list):
        return
    records = frames
    frame_count = len(records)
    totalTime = records[frame_count - 1].timestamp - records[0].timestamp
    print('total time = %.2f' % (totalTime))

    roadId, laneOfEgo = getRoadIdAndLaneId(str(records[0].ego.land_id))
    recordTemp = records[0]

    actors = {}
    # 周边车辆
    cars = {}

    laneChangeEvents = []

    # 计算ego相关属性
    index = 0
    for record in records:
        # find lane changed
        _, tempLane = getRoadIdAndLaneId(record.ego.land_id)
        if not str(tempLane) == laneOfEgo:
            laneChangeSpendTime = 2
            laneChangeStartTime = (record.timestamp - records[0].timestamp) - laneChangeSpendTime / 3.0
            print('find ego lane changed, frameIndex=%d, from (time = %.0f, ego = %s) to (time = %.0f, ego = %s)' % (
                index, recordTemp.timestamp, recordTemp.ego, record.timestamp, record.ego))
            if len(laneChangeEvents) > 0:
                lastEvent = laneChangeEvents[len(laneChangeEvents) - 1]
                if laneChangeStartTime - lastEvent.beginTime < laneChangeSpendTime:
                    lastEvent.spendTime = 1.5
                    laneChangeStartTime = lastEvent.beginTime + lastEvent.spendTime
                    laneChangeSpendTime = 1.5

            laneChangeEvents.append(LaneChangeEvent(laneChangeStartTime, laneChangeSpendTime, laneOfEgo, tempLane))
        laneOfEgo = tempLane
        recordTemp = record

        # print(len(record.objects.object.cars))

        for car in record.objects.object.cars:
            # print(car.id)
            if not cars.__contains__(car.id):
                cars[car.id] = []
            cars[car.id].append(car)

        index += 1

    # 检测ego车速变化
    speedList = []
    timestampList = []

    for record in records:
        speedList.append(record.ego.speed)
        timestampList.append(record.timestamp)
    speedChangeEvents = _findSpeedChangeEvents(speedList, timestampList)

    roadId, laneId = getRoadIdAndLaneId(frames[0].ego.land_id)
    actors[EGO_ID] = Actor(EGO_ID, 0, frames[0].ego.speed / 3.6, laneId, roadId)

    for key, value in cars.items():
        # findLaneChanged(value)
        # findCarSpeed(value)
        velo = actors[EGO_ID].initSpeed + (
            math.sqrt(pow(value[1].x - value[0].x, 2) + pow(value[1].y - value[0].y, 2))) / (
                       value[1].timestamp - value[0].timestamp)
        if key == 995:
            velo -= 2
        s = math.sqrt(pow(value[0].x, 2) + pow(value[0].y, 2))
        roadId, landId = getRoadIdAndLaneId(value[0].lane_id)
        actors[key] = Actor(key, s, velo, landId, roadId)

    return _createXoscWith(xodrFileName, 0.5, speedChangeEvents, actors, laneChangeEvents, totalTime + 2)


def _createXoscWith(xodrFileName, timeBegin, speedChangeEvents, actors, laneChangeEvents, totalTime=15):
    print('createXoscWith !!!\ntimeBegin=%s,\nspeedChangeEvents=%s,\nactors={%s},\nlaneChangeEvents={%s}' % (
        timeBegin, "\n".join([str(v) for v in speedChangeEvents]), "\n".join([str(v) for _, v in actors.items()]),
        "\n".join([str(x) for x in laneChangeEvents])
    ))
    # create catalogs
    catalog = xosc.Catalog()
    catalog.add_catalog('VehicleCatalog', VEHICLE_CATALOG)

    # create road
    road = xosc.RoadNetwork(roadfile=xodrFileName, scenegraph='')

    # create parameters
    paramdec = xosc.ParameterDeclarations()

    # create entities
    egoName = actors[EGO_ID].name
    otherAct = []
    for key, value in actors.items():
        if not key == EGO_ID:
            otherAct.append(value)

    # target1Name = otherAct[0].name
    # target2Name='target2'
    # target3Name='target3'

    entities = xosc.Entities()
    entities.add_scenario_object(
        egoName, xosc.CatalogReference('VehicleCatalog', 'car_white'))

    size = len(carCatalog)
    for i in range(len(otherAct)):
        target = otherAct[i]
        carColor = carCatalog[i % size]
        entities.add_scenario_object(target.name, xosc.CatalogReference('VehicleCatalog', carColor))

    # entities.add_scenario_object(target2Name,xosc.CatalogReference('VehicleCatalog','car_yellow'))
    # entities.add_scenario_object(target3Name,xosc.CatalogReference('VehicleCatalog','car_yellow'))

    # create init

    init = xosc.Init()

    init.add_init_action(egoName, xosc.TeleportAction(
        xosc.LanePosition(actors[EGO_ID].initPosition, 0, actors[EGO_ID].initLane, actors[EGO_ID].initRoad)))
    init.add_init_action(egoName, xosc.AbsoluteSpeedAction(actors[EGO_ID].initSpeed, xosc.TransitionDynamics(
        xosc.DynamicsShapes.step, xosc.DynamicsDimension.time, 1)))

    for target in otherAct:
        init.add_init_action(target.name, xosc.TeleportAction(
            xosc.LanePosition(target.initPosition, 0, target.initLane, target.initRoad)))
        init.add_init_action(target.name, xosc.AbsoluteSpeedAction(target.initSpeed,
                                                                   xosc.TransitionDynamics(xosc.DynamicsShapes.step,
                                                                                           xosc.DynamicsDimension.time,
                                                                                           1)))

    ## create the maneuver
    man = xosc.Maneuver('my_maneuver')

    # create the speed up action
    for i in range(len(speedChangeEvents)):
        speedChange = speedChangeEvents[i]
        speedUpEvent = xosc.Event('speedchange' + str(i), xosc.Priority.parallel)
        speedUpEvent.add_action('speedaction' + str(i), xosc.AbsoluteSpeedAction(speedChange.targetSpeed,
                                                                                 xosc.TransitionDynamics(
                                                                                     xosc.DynamicsShapes.linear,
                                                                                     xosc.DynamicsDimension.time,
                                                                                     speedChange.spendTime)))

        # create an event for target
        # trigcond = xosc.SimulationTimeCondition(timeBegin, xosc.Rule.greaterThan)
        trigger = xosc.ValueTrigger('starttrigger' + str(i), 0.2, xosc.ConditionEdge.rising,
                                    xosc.SimulationTimeCondition(speedChange.beginTime, xosc.Rule.greaterThan))

        speedUpEvent.add_trigger(trigger)
        man.add_event(speedUpEvent)

    # create lane change event

    for index in range(len(laneChangeEvents)):
        laneChangeEvent = laneChangeEvents[index]
        lane_change_event = xosc.Event('lanechange' + str(index), xosc.Priority.parallel)
        lane_change_event.add_action('lanechangeaction' + str(index),
                                     xosc.AbsoluteLaneChangeAction(laneChangeEvent.endLaneId, xosc.TransitionDynamics(
                                         xosc.DynamicsShapes.sinusoidal, xosc.DynamicsDimension.time,
                                         laneChangeEvent.spendTime)))
        lane_change_event.add_trigger(xosc.ValueTrigger(
            'starttrigger' + str(index), 0.2, xosc.ConditionEdge.rising,
            xosc.SimulationTimeCondition(laneChangeEvent.beginTime, xosc.Rule.greaterThan)))
        man.add_event(lane_change_event)

    mangr = xosc.ManeuverGroup('mangroup')
    mangr.add_actor(egoName)
    mangr.add_maneuver(man)

    # create act
    triggerForAct = xosc.ValueTrigger('CutInActStart', 0, xosc.ConditionEdge.rising,
                                      xosc.SimulationTimeCondition(0, xosc.Rule.greaterThan))
    act = xosc.Act('CutIn', triggerForAct)
    act.add_maneuver_group(mangr)

    ## create the story
    storyparam = xosc.ParameterDeclarations()
    # storyparam.add_parameter(xosc.Parameter('$owner',xosc.ParameterType.string,target1Name))
    story = xosc.Story('mystory', storyparam)
    story.add_act(act)

    ## create the storyboard
    sb = xosc.StoryBoard(init, xosc.ValueTrigger('stop_simulation', 0, xosc.ConditionEdge.rising,
                                                 xosc.SimulationTimeCondition(totalTime, xosc.Rule.greaterThan),
                                                 'stop'))
    sb.add_story(story)

    ## create the scenario
    sce = xosc.Scenario('cut_in_example', 'Boning', paramdec, entities=entities, storyboard=sb, roadnetwork=road,
                        catalog=catalog)

    sce.write_xml(os.path.basename(__file__).replace('.py', '.xosc'))
    fileName = os.path.basename(__file__).replace('.py', '.xosc')
    return fileName


def _findSpeedChangeEvents(speedList, timestampList):
    speedChangeEvents = []
    count = len(speedList)
    print('speed list = ' + str(speedList))
    if count > 1:
        a = []
        for i in range(1, count):
            a.append(speedList[i] - speedList[i - 1])

        lastA = a[0]
        lastIndex = 1
        if lastA > 0.001:
            lastState = SpeedChangeState.speed_up
        elif lastA < -0.001:
            lastState = SpeedChangeState.slow_down
        else:
            lastState = SpeedChangeState.uniform
        for i in range(len(a)):

            if a[i] > 0.001:
                curState = SpeedChangeState.speed_up
            elif a[i] < -0.001:
                curState = SpeedChangeState.slow_down
            else:
                curState = SpeedChangeState.uniform

            if curState != lastState or i == len(a) - 1:
                event = SpeedChangeEvent(timestampList[lastIndex] - timestampList[0],
                                         timestampList[i - 1] - timestampList[lastIndex], speedList[i - 1] / 3.6)
                speedChangeEvents.append(event)
                lastIndex = i - 1
                lastState = curState
                print('speed change event:' + str(event))

    return speedChangeEvents


class Actor:
    # speed m/s
    def __init__(self, name, initPosition, initSpeed, initLane, initRoad):
        self.name = str(name)
        self.initPosition = initPosition
        self.initSpeed = initSpeed
        self.initLane = int(initLane)
        self.initRoad = int(initRoad)

    def __str__(self):
        return '{name=%s,initPosition=%d,initSpeed=%f,initLane=%d,initRoad=%d}' % (
            self.name, self.initPosition, self.initSpeed, self.initLane, self.initRoad)


class SpeedChangeEvent:
    # targetSpeed m/s
    def __init__(self, beginTime, spendTime, targetSpeed):
        self.beginTime = beginTime
        self.spendTime = spendTime
        self.targetSpeed = targetSpeed

    def __str__(self):
        return '{beginTIme=%s, spendTime=%s, targetSpeed=%s}' % (
            str(self.beginTime), str(self.spendTime), str(self.targetSpeed))


class SpeedChangeState(Enum):
    speed_up = auto()
    slow_down = auto()
    uniform = auto()


class LaneChangeEvent:
    def __init__(self, beginTime, spendTime, beginLaneId, endLaneId, ):
        self.beginTime = beginTime
        self.beginLaneId = beginLaneId
        self.endLaneId = endLaneId
        self.spendTime = spendTime

    def __str__(self):
        return '{beginTime=%s, spendTime=%s, from %s to %s}' % (
            str(self.beginTime), str(self.spendTime), str(self.beginLaneId), str(self.endLaneId))
