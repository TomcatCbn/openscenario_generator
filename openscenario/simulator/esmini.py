import os
from .constants import ESMINI_PATH
from .constants import ESMINI_SAMPLE_PATH


def recordGif(xodrFileName, xoscFileName, total_time):
    __exec_cmd('mv %s %s' % (xodrFileName, ESMINI_SAMPLE_PATH))
    __exec_cmd('mv %s %s' % (xoscFileName, ESMINI_SAMPLE_PATH))
    __exec_cmd('LENGTH=%d' % total_time)

    __exec_cmd('Xvfb :1 -screen 0 ${RESOLUTION}x24 &> xvfb.log &')
    gif_name = xoscFileName.replace('.xosc', '.gif')
    esmini_cmd = 'timeout $LENGTH esmini --osc %s%s --window 0 0 ${RESOLUTION//x/ } --camera_mode top &' % (
        ESMINI_SAMPLE_PATH, xoscFileName)
    __exec_cmd(esmini_cmd)

    __exec_cmd('avconv -f x11grab -s $RESOLUTION -r $FRAMERATE -t $LENGTH -y -i :1.0 \"%s\"' % gif_name)

    return '%s%s' % (ESMINI_SAMPLE_PATH, gif_name)


def __exec_cmd(s):
    print('exec cmd ' + s)
    os.system(s)
