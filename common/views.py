import json
import logging
import os
from pprint import pprint
from urllib.parse import urlencode, quote
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from config.settings import base
from .forms import UserForm
from .urlopen_try_except import urlopen_request
from .social_user_signup import social_user_signup
from django.contrib.auth.models import User
import logging

logger = logging.getLogger('chemblog')


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


secret_file = os.path.join(base.BASE_DIR, 'secrets.json')
with open(secret_file) as f:
    secrets = json.loads(f.read())


def redirect_sociallogin(env, provider):
    local = 'http://127.0.0.1:8000/common/'
    prod = 'https://chemia.kr/common/'
    if provider == 'kakao':
        path = 'kakaocallback'
    elif provider == 'naver':
        path = 'navercallback'
    return local if env == 'local' else prod, path


def kakaologin(request):
    client_id = base.get_secret('client_id_kakao')
    host_with_protocol, path = redirect_sociallogin(request.get_host()[:5], 'kakao')
    redirect_uri = host_with_protocol + path
    url = f'https://kauth.kakao.com/oauth/authorize' \
          f'?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}'
    return redirect(url)


def kakaocallback(request, headers=None):
    client_id = base.get_secret('client_id_kakao')
    host_with_protocol, path = redirect_sociallogin(request.get_host()[:5], 'kakao')
    redirect_uri = host_with_protocol + path
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

    return redirect('common:signup_kakao', access_token)
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

    user = social_user_signup(username, email)
    
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    return redirect('chemblog:index')


def naverlogin(request):
    client_id = base.get_secret('client_id_naver')
    host_with_protocol, path = redirect_sociallogin(request.get_host()[:5], 'naver')
    redirect_uri = host_with_protocol + path
    urlencoded_redirect_uri = quote(redirect_uri)
    state_stirng = request.POST.get('csrfmiddlewaretoken')

    base.update_secret('state', state_stirng)

    url_naverlogin = f'https://nid.naver.com/oauth2.0/authorize?response_type=code&' \
                     f'client_id={client_id}&state={state_stirng}&redirect_uri={urlencoded_redirect_uri}'
    return redirect(url_naverlogin)


def inner_urlopen(url, data):
    try:
        with urlopen(url, bytes(data, encoding='utf-8')) as response:
            body = response.read()
    except HTTPError as error:
        print(error.status, error.reason)
    except URLError as error:
        print(error.reason)
    else:
        res_as_dic = json.loads(body)
        return res_as_dic


def navercallback(request):
    # 네이버 로그인 버튼을 눌렀을 때 전달된 csrf token
    csrf_token = base.get_secret('state')

    logger.info(csrf_token, request.GET.get('state'))

    # 위의 토큰 값과 콜백으로 전달 받은 토큰값 일치 여부
    if csrf_token == request.GET.get('state'):
        url = 'https://nid.naver.com/oauth2.0/token'
        params = {
            'grant_type': 'authorization_code',
            'client_id': base.get_secret('client_id_naver'),
            'client_secret': base.get_secret('client_secret_naver'),
            'code': request.GET.get('code'),
        }
        data = urlencode(params)
        response = inner_urlopen(url, data)
        access_token = response['access_token']
        return redirect('common:signup_naver', access_token)
    else:
        return render(request, 'common/400.html')


def signup_naver(request, access_token):
    url = 'https://openapi.naver.com/v1/nid/me'
    authorization = f'Bearer {access_token}'
    req = Request(url, headers={'Authorization': authorization})
    resp_as_dic = urlopen_request(req)
    pprint(resp_as_dic)
    username = resp_as_dic['response']['nickname']
    email = resp_as_dic['response']['email']

    user = social_user_signup(username, email)
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    return redirect('chemblog:index')


def naverlogin_reprompt(request):
    client_id = base.get_secret('client_id_naver')
    host_with_protocol, path = redirect_sociallogin(request.get_host()[:5], 'naver')
    redirect_uri = host_with_protocol + path
    urlencoded_redirect_uri = quote(redirect_uri)
    state_string = request.POST.get('csrfmiddlewaretoken')

    base.update_secret('state', state_string)

    url_reprompt = f'https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={client_id}&' \
                   f'state={state_string}&redirect_uri={urlencoded_redirect_uri}&auth_type=reprompt'

    return redirect(url_reprompt)


def user_profile(request):
    user = User.objects.get(id=request.user.id)
    user_post = user.author_post.all()
    user_comment = user.author_comment.all()
    context = {
        'user_post': user_post,
        'user_comment': user_comment
    }
    return render(request, 'common/user_profile.html', context)


def page_not_found(request, exception):
    return render(request, 'common/404.html', {})


def server_error(request):
    return render(request, 'common/500.html', {})

