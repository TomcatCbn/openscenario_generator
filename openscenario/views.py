from django.http import HttpResponse
# Create your views here.
from rest_framework.renderers import JSONRenderer

from .traffic_stream_parse import handle


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


# class XMLResponse(HttpResponse):
#     def __init__(self, path, **kwargs):
#         render


def convert_open_scenario(request):
    xord, xosc = handle()
    with open(xosc, 'r', encoding='UTF-8') as f:
        xosc_content = f.read()
    with open(xord, 'r', encoding='UTF-8') as f:
        xord_content = f.read()
    content = '%s\n%s' % (xord_content, xosc_content)
    return HttpResponse(content=xord_content, content_type='application/xml')

    # 返回文件，可下载
    # file = file_iterator(xosc)
    # response = StreamingHttpResponse(file)
    # response['Content-Type'] = 'application/xml'
    # response['Content-Disposition'] = 'attachment; filename={0}'.format(quote(xosc))
    # return response


def convert_open_drive(request):
    return handle()
