#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from apps.site.forms import FeedbackForm
from apps.topic.models import Topic, Node, ParentNode
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.aggregates import Count
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
import datetime
#from main.models import WHOOSH_SCHEMA

def index(request):
    context = {}
    topic_list = Topic.objects.all().order_by('-updated_on')[:41]
    if topic_list.count() == 41:
        more = True
    else:
        more = False
    context['topics'] = topic_list[:40]
    context['more'] = more
    all_nodes = []
    parent_nodes = ParentNode.objects.all()
    for item in parent_nodes:
        node = {}
        children_nodes = Node.objects.filter(category=item.id)
        node['parent'] = item.name
        node['nodes'] = children_nodes
        all_nodes.append(node)
    context['all_nodes'] = all_nodes
    time_now = datetime.datetime.now()
    from_date = time_now - datetime.timedelta(days=7)
    hot_topics = Topic.objects.filter(created_on__range=[from_date, time_now]).order_by('-num_replies')[:10]
    context['hot_topics'] = hot_topics
    hot_nodes = Node.objects.filter(num_topics__gt=0,updated_on__gt=from_date).order_by('-updated_on')[:10]
    context['hot_nodes'] = hot_nodes
    return render(request,'index.html',context)

def star(request):
    context = {}
    time_now = datetime.datetime.now()
    from_date = time_now - datetime.timedelta(days=7)
    hot_topics = Topic.objects.filter(created_on__range=[from_date, time_now]).order_by('-num_replies')[:10]
    context['hot_topics'] = hot_topics
    hot_nodes = Node.objects.filter(num_topics__gt=0,updated_on__gt=from_date).order_by('-updated_on')[:10]
    context['hot_nodes'] = hot_nodes
    
    from_date2 = time_now - datetime.timedelta(days=30)
    topic_list = Topic.objects.filter(updated_on__range=[from_date2, time_now],likes__isnull=False).annotate(likes_count=Count('likes')).order_by('-likes_count')[:40]
    #topic_list = sorted(topic_list, key=lambda x: x.likes.all().count(), reverse=True)
    
    context['topics'] = topic_list
    
    all_nodes = []
    parent_nodes = ParentNode.objects.all()
    for item in parent_nodes:
        node = {}
        children_nodes = Node.objects.filter(category=item.id)
        node['parent'] = item.name
        node['nodes'] = children_nodes
        all_nodes.append(node)
    context['all_nodes'] = all_nodes
    
    return render(request,'star.html',context)

def recent(request):
    context = {}
    topic_list = Topic.objects.all().order_by('-updated_on')
    paginator = Paginator(topic_list, 5)

    page = request.GET.get('page')
    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        topics = paginator.page(1)
    except EmptyPage:
        topics = paginator.page(paginator.num_pages)
    context['topics'] = topics
    return render(request,'recent.html',context)

#def search(request):
#     context = {}
# #     p = Topic(title='first post', body='This is my first post')
# #     p.save() # The new model is already added to the index
#     if request.method =='GET':
#         get = request.GET.copy()
#         if get.has_key('q'):
#             query = get['q']
#             hits = Topic.objects.query(query)
#             
#             context['query'] = query
#             context['hits'] = hits
#     return render(request,'search.html',context)
# 
# """
#     Simple search view, which accepts search queries via url, like google.
#     Use something like ?q=this+is+the+serch+term
# 
#     """
#    context = {}
#     storage = FileStorage(settings.WHOOSH_INDEX)
#     ix = index.Index(storage, schema=WHOOSH_SCHEMA)
#     ix = create_in(settings.WHOOSH_INDEX, WHOOSH_SCHEMA)
#     hits = []
#     query = request.GET.get('q', None)
#     if query is not None and query != u"":
#         # Whoosh don't understands '+' or '-' but we can replace
#         # them with 'AND' and 'NOT'.
#         #query = query.replace('+', ' AND ').replace(' -', ' NOT ')
#         context['query'] = query
#         parser = QueryParser("content", schema=ix.schema)
#         try:
#             qry = parser.parse(query)
#         except:
#             # don't show the user weird errors only because we don't
#             # understand the query.
#             # parser.parse("") would return None
#             qry = None
#         if qry is not None:
# #             searcher = ix.searcher()
# #             hits = searcher.search(qry)
#             with ix.searcher() as searcher:
#                 hits = searcher.find('content', u'哈')
#                  
#                 #hits = searcher.search(qry)
#                 context['hits'] = hits
#             
#     return render(request,'search.html',context)

def about(request):
    return render(request,'about.html')

def zen(request):
    return render(request,'zen.html')

def feedback(request):
    if request.method == 'GET':
        context = {}
        form = FeedbackForm()
        context['form'] = form
        return render(request,'feedback.html',context)
    form = FeedbackForm(request.POST)
    if form.is_valid():
        feedback = form.save(commit=False)
        if request.user.is_authenticated():
            feedback.author = request.user
        else:
            feedback.author = None
        feedback.save()
    return HttpResponseRedirect('/feedback/success')

def feedback_success(request):
    return render(request,'feedback_success.html')

def help_use(request):
    return render(request,'help.html')

def one(request):
    return render(request,'one.html')

def people(request):
    context = {}
    peoples = User.objects.filter(is_active=True).order_by('date_joined')
    paginator = Paginator(peoples, 30)
    page = request.GET.get('page')
    try:
        people_list = paginator.page(page)
    except PageNotAnInteger:
        people_list = paginator.page(1)
    except EmptyPage:
        people_list = paginator.page(paginator.num_pages)
    context['people_list'] = people_list
    return render(request,'people_list.html',context)