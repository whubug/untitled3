# -*- coding: utf-8 -*-

# from django.http import HttpResponse
from django.shortcuts import render


def hello(request):
    context = {}
    context['hello'] = 'Hello World!'
    return render(request, 'hello.html', context)


def testlayui(request):
    return render(request, 'base2.html')


def testlayui2(request):
    return render(request, 'ansible.html')