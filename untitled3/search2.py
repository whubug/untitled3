# -*- coding: utf-8 -*-

from django.shortcuts import render,render_to_response
from django.views.decorators import csrf

from ansible_api import ansibleRun
from TestModel.models import Item


# 接收POST请求数据
def search_post(request):
    ctx = {}
    if request.POST:
        host = request.POST['host']
        module = request.POST['module']
        args = request.POST['args']
        ctx['rlt'] = host
        ctx['module'] = module
        ctx['args'] = args

        ctx['out'] = ansibleRun(host, module, args)
        item = Item()
        item.host = host
        item.args = args
        item.module = module
        item.save()
        ctx['output'] = Item.objects.filter(host='192.168.79.132')
    return render(request, "ansible.html", ctx)


def login(request):
    ctx = {}

    if request.POST:
        name = request.POST['usrname']
        print name
        password = request.POST['psw']
        ctx['name'] = name
        return render(request, "post.html", ctx)
    return render(request, "login.html")