from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from .schema import schema
from graphql.execution.execute import execute
import json

def index(request):
    query = request.GET.get('query')
    result = execute(schema, query, context_value=request)
    return HttpResponse(json.dumps(result.data), content_type='application/json')