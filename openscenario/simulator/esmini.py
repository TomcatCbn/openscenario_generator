import os
from .constants import ESMINI_CMD_PATH
from .constants import ESMINI_SAMPLE_PATH
import os


def record_gif(xodr_file_name, xosc_file_name, total_time):
    if not os.path.exists(ESMINI_SAMPLE_PATH):
        os.mkdir(ESMINI_SAMPLE_PATH)

    __exec_cmd('mv %s %s' % (xodr_file_name, ESMINI_SAMPLE_PATH))
    __exec_cmd('mv %s %s' % (xosc_file_name, ESMINI_SAMPLE_PATH))
    __exec_cmd('LENGTH=%d' % total_time)

    __exec_cmd('Xvfb :1 -screen 0 ${RESOLUTION_X}x${RESOLUTION_Y}x24 &> xvfb.log &')
    gif_name = xosc_file_name.replace('.xosc', '.gif')
    esmini_cmd = 'timeout $LENGTH %s --osc %s%s --window 0 0 ${RESOLUTION_X} ${RESOLUTION_Y} --camera_mode top &' % (
        ESMINI_CMD_PATH, ESMINI_SAMPLE_PATH, xosc_file_name)
    __exec_cmd(esmini_cmd)

    __exec_cmd(
        'avconv -f x11grab -s ${RESOLUTION_X}x${RESOLUTION_Y} -r $FRAMERATE -t $LENGTH -y -i :1.0 \"%s\"' % gif_name)

    return '%s%s' % (ESMINI_SAMPLE_PATH, gif_name)


def __exec_cmd(s):
    print('exec cmd ' + s)
    os.system(s)
