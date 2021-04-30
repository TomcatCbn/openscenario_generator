from urllib.parse import quote
from django.http import HttpResponse, StreamingHttpResponse
# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer

from openscenario.utils.fileutil import file_iterator
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

@api_view(['GET'])
def convert_open_scenario(request):
    type = request.query_params.get('type')
    download = request.query_params.get('download')
    xord, xosc, gif = handle('gif' == type)
    file_path=''
    if 'xord' == type:
        content_type = 'application/xml'
        file_path= xord
    elif 'gif' == type:
        content_type = 'image/gif'
        file_path = gif
    else:
        content_type = 'application/xml'
        file_path = xosc

    if download:
        # 返回文件，可下载
        file = file_iterator(file_path)
        response = StreamingHttpResponse(file)
        response['Content-Type'] = 'application/xml'
        response['Content-Disposition'] = 'attachment; filename={0}'.format(quote(xosc))
        return response
    else:
        with open(file_path, 'r', encoding='UTF-8') as f:
            content = f.read()
        return HttpResponse(content=content, content_type=content_type)
