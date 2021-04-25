from six import BytesIO

from snippets.models import Snippet
from snippets.serializers import SnippetSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

snippet = Snippet(code='foo = "bar"\n')
snippet.save()

snippet = Snippet(code='print "hello, world"\n')
snippet.save()

serializer = SnippetSerializer(snippet)
serializer.data

content = JSONRenderer().render(serializer.data)
content

stream = BytesIO(content)
data = JSONParser().parse(stream)
