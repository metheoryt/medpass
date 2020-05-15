import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import requests

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from meduserstore.settings import BASE_DIR

@csrf_exempt
def validate_merchant(request):
    if request.method == 'POST':
        url = request.POST['validation_url']
        rs = requests.post(url, json={
            "merchantIdentifier": "merchant.com.wooppay.processing",
            "displayName": "Wooppay LLC",
            "initiative": "web",
            "initiativeContext": "wopay.tk"
        }, cert=(os.path.join(BASE_DIR, 'merchantId.crt.pem'), os.path.join(BASE_DIR, 'merchantId.key.pem')))
        return JsonResponse(rs.json())
