from django.http import HttpResponse
# Create your views here.
from rest_framework.decorators import api_view
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

@api_view(['GET'])
def convert_open_scenario(request):
    type = request.query_params.get('type')
    print(type)
    xord, xosc, gif = handle('gif' == type)

    if 'xord' == type:
        with open(xord, 'r', encoding='UTF-8') as f:
            content = f.read()
            content_type = 'application/xml'
    elif 'gif' == type:
        with open(gif, 'rb') as f:
            content = f.read()
            content_type = 'image/gif'
    else:
        with open(xosc, 'r', encoding='UTF-8') as f:
            content = f.read()
            content_type = 'application/xml'

    return HttpResponse(content=content, content_type=content_type)

    # 返回文件，可下载
    # file = file_iterator(xosc)
    # response = StreamingHttpResponse(file)
    # response['Content-Type'] = 'application/xml'
    # response['Content-Disposition'] = 'attachment; filename={0}'.format(quote(xosc))
    # return response
