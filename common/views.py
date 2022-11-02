import json
import os
from pprint import pprint
from urllib.parse import urlencode
from urllib.request import Request

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from config import settings
from .forms import UserForm
from django.http import HttpResponse
from .urlopen_try_except import urlopen_request
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=raw_password)
            login(request, user)
            return redirect('chemblog:index')
    else:
        form = UserForm()
    return render(request, 'common/signup.html', {'form': form})


secret_file = os.path.join(settings.BASE_DIR, 'secrets.json')
with open(secret_file) as f:
    secrets = json.loads(f.read())

client_id = settings.get_secret('client_id')
redirect_uri = 'http://127.0.0.1:8000/common/kakaocallback'


def kakaologin(request):
    url = f'https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}'
    return redirect(url)


def kakaocallback(request, headers=None):
    code = request.GET.get('code')
    print(code)
    url = 'https://kauth.kakao.com/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'redirection_uri': redirect_uri,
        'code': code
    }
    encdata = urlencode(data)
    postdata = encdata.encode('utf-8')
    request = Request(url, headers=headers or {}, data=postdata)

    resp_as_dic = urlopen_request(request)
    access_token = resp_as_dic['access_token']

    return redirect('common:signup_kakao', access_token=access_token)
    # with 구문을 사용치 않아 (HTTPResponse 객체가 opening 후에 closing이 안되어) 에러가 난것으로 알았으나 다음과 같이 with 없는 코드
    # 로도 위의 코드와 같은 결과를 얻음
    '''response = urlopen(request, timeout=10)
        body = response.read()
        response_json = body.decode('utf-8')
        response_dic = json.loads(response_json)
        access_token = response_dic['access_token']
        print(f'access_token : {access_token}')
        return redirect('chemblog/index')'''


def signup_kakao(request, access_token):
    url = "https://kapi.kakao.com/v2/user/me"
    authorization = f'Bearer ${access_token}'
    headers = {"Authorization": authorization}
    req = Request(url, headers=headers)

    resp_as_dic = urlopen_request(req)
    pprint(resp_as_dic)

    username = resp_as_dic['properties']['nickname']
    email = resp_as_dic['kakao_account']['email']

    try:
        user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        user = User.objects.create_user(username, email)
        user.set_unusable_password()
        user.save()
    
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    return redirect('chemblog:index')
