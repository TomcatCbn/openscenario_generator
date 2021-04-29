import os

from .constants import ESMINI_CMD_PATH
from .constants import ESMINI_SAMPLE_PATH


def record_gif(xodr_file_name, xosc_file_name, length=10, resolution_x=320, resolution_y=240, frame_rate=10):
    if not os.path.exists(ESMINI_SAMPLE_PATH):
        os.mkdir(ESMINI_SAMPLE_PATH)

    __exec_cmd('mv %s %s' % (xodr_file_name, ESMINI_SAMPLE_PATH))
    __exec_cmd('mv %s %s' % (xosc_file_name, ESMINI_SAMPLE_PATH))
    print('gif configs, length=%s, resolution=%sx%s, frame_rate=%s' % (
        str(length), str(resolution_x), str(resolution_y), str(frame_rate)))

    __exec_cmd('Xvfb :1 -screen 0 %dx%dx24 -nocursor &> xvfb.log &' % (resolution_x, resolution_y))
    gif_name = xosc_file_name.replace('.xosc', '.gif')
    esmini_cmd = 'timeout %d %s --osc %s%s --window 0 0 %d %d --camera_mode top &' % (
        length, ESMINI_CMD_PATH, ESMINI_SAMPLE_PATH, xosc_file_name, resolution_x, resolution_y)
    __exec_cmd(esmini_cmd)
    gif_save_path = ESMINI_SAMPLE_PATH + '/' + gif_name
    __exec_cmd(
        'avconv -f x11grab -s %dx%d -draw_mouse 0 -r %d -t %d -y -i :1.0 \"%s\"' % (
            resolution_x, resolution_y, frame_rate, length, gif_save_path))

    return gif_save_path


def __exec_cmd(s):
    print('exec cmd ' + s)
    os.system(s)
