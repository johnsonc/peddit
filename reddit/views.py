from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django import newforms as forms
from django.newforms import form_for_model
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from django import oldforms as oldforms
from django.contrib.auth.forms import UserCreationForm
from django.utils.html import escape
from MySQLdb import IntegrityError #Todo

from reddit.models import Link
from reddit.models import Comment
from reddit.models import UserVotes, SavedLink, Tags
from reddit import defaults

import random
import datetime
import time
from urlparse import urlparse

def index(request):
            
    data = []
    links = Link.objects.all().order_by('-points', '-added_on')
    links, page = paginate_links(request, links)
    for link in links:
      print _populate_link_data(link, request.user)
      data.append(link)
      #db_data.append(link.link)                
    return render_to_response('index.html', {'links':data, 'page':page, }, context_instance=RequestContext(request))
    
def show_details(request, link_id, off = 0):        
    try:
        off = request.GET['offset']
    except:
        off = '0'
    off = eval(off)    
    last = off+defaults.comments_per_page
    page = {}  
                
    request.session['link_id'] = link_id
    link = Link.objects.get(id=link_id)
    _populate_link_data(link, request.user)
    comments = Comment.objects.filter(link = link)[off:last]
    _populate_comments_data(comments)
    comment_form = submit_comment(request)   
    tag_form = tag_link(request)
    tags = Tags.objects.filter(link = link) 
    print 'foo'     
 
    
    if off > 0:
        page['has_prev'] = True
        page['prev'] = off - defaults.comments_per_page
    if last < Comment.objects.filter(link = link).count():
        page['has_next'] = True
        page['next'] = off + defaults.comments_per_page 
           
    if request.method == 'POST':
        return HttpResponseRedirect('.')
    return render_to_response('details.html', {'link':link, 'comments':comments, 'comment_form':comment_form, 'tag_form':tag_form, 'tags': tags, 'page':page, 'link_id':link_id}, context_instance=RequestContext(request))
 

def show_tagged_links(request, tag_text):
        
    tags = Tags.objects.filter(tag = tag_text)
    tags, page = paginate_links(request, tags)
    links = []
    for tag in tags:
        links.append(tag.link)
    _populate_links_data(links, request.user)
    
            
    return render_to_response('index.html', {'links':links, 'page':page}, context_instance=RequestContext(request))
        
def user_details(request, user_name = None,):        
    
    if user_name == None:
        user_name = request.user.username
        subtitle = 'Your submitted links'
        otherprofile  = False  
    else:
        subtitle = "%s's submitted links" % user_name
        otherprofile  = True 
    user = User.objects.get(username = user_name)
    links = Link.objects.filter(user = user)[:10]
    _populate_links_data(links, request.user)
    
    return render_to_response('user.html', {'links':links, 'subtitle':subtitle, 'otherprofile':otherprofile, 'user_name':user_name}, context_instance=RequestContext(request))    

def saved_links(request, user_name = None, ):      
    if user_name == None:
        user_name = request.user.username
        subtitle = 'Your saved links' 
        otherprofile  = False          
    else:
        subtitle = "%s's saved links" % user_name
        otherprofile  = True         
    user = User.objects.get(username = user_name)
    voted_links = SavedLink.objects.filter(user = user)
    voted_links, page = paginate_links(request, voted_links,)
    links = [el.link for el in voted_links]
    _populate_links_data(links, request.user)
    
    return render_to_response('user.html', {'links':links, 'page':page, 'subtitle': subtitle, 'otherprofile':otherprofile, 'user_name':user_name}, context_instance=RequestContext(request))
        
def liked_links(request, up, user_name = None, ):       
    if user_name == None:
        user_name = request.user.username
        greet = 'Your'
        otherprofile  = False          
    else:
        greet = "%s's" % user_name
        otherprofile  = True         
    user = User.objects.get(username = user_name)
    voted_links = UserVotes.objects.filter(user = user, upvote = up)
    voted_links, page = paginate_links(request, voted_links,)
    links = [el.link for el in voted_links]
    _populate_links_data(links, request.user)
    if up:
        subtitle = '%s liked links' % greet
    else:
        subtitle = '%s disliked links' % greet
    return render_to_response('user.html', {'links':links, 'page':page, 'subtitle':subtitle, 'otherprofile':otherprofile, 'user_name':user_name}, context_instance=RequestContext(request))

def paginate_links(request, query_set):
    maximum = query_set.count()
    try:
        off = request.GET['offset']
    except:
        off = '0'
    off = eval(off)    
    last = off+defaults.links_per_page
    page = {}  
    paged_query_set = query_set[off:last]        
    
    if off > 0:
        page['has_prev'] = True
        page['prev'] = max(off - defaults.links_per_page, 0)
    if last < maximum:
        print 'hol'
        page['has_next'] = True
        page['next'] = off + defaults.links_per_page 
        
    return paged_query_set, page
    
def show_comment(request, comment_id):
    comments = Comment.objects.filter(id = comment_id)
    _populate_comments_data(comments)    
    return render_to_response('comment.html', {'comments': comments, 'otherprofile':otherprofile}, context_instance=RequestContext(request))

def user_comments(request, user_name = None):    
    if user_name == None:
        user_name = request.user.username
        subtitle = "Your comments"
        otherprofile  = False  
    else:
        subtitle = "%s comments" % user_name
        otherprofile  = True 
    user = User.objects.get(username = user_name)
    comments = Comment.objects.filter(user = user)
    _populate_comments_data(comments)        
    return render_to_response('comment.html', {'comments': comments, 'subtitle':subtitle, 'otherprofile':otherprofile }, context_instance=RequestContext(request))
    

@login_required
def vote_link(request, link_id, up):
    link = Link.objects.get(id = link_id)
    voted = link.vote(request.user, up)                  
    if voted == True:
            return HttpResponse(str(link.id))
    return HttpResponse(str(-1))


@login_required
def submit_link(request):
    class SubmitLink(forms.Form):
        link = forms.URLField()
        text = forms.CharField(widget=forms.Textarea)
    if request.method == 'GET':
        sub_f = SubmitLink()
        return render_to_response('submit.html', {'sub_f': sub_f,}, context_instance=RequestContext(request))
    elif request.method =='POST':
        try:
            sub_f = SubmitLink(request.POST)
            if sub_f.is_valid():
                link = request.POST['link']
                text = request.POST['text']
                user_id = request.user
                the_link = Link.objects.create_link(link = link, text = text, user = user_id)
                the_link.save()  
                return HttpResponseRedirect(the_link.get_absolute_url())      
            else:
                return render_to_response('submit.html', {'sub_f': sub_f,})
        except IntegrityError:
            links = Link.objects.filter(link = link)
            for the_link in links:
                return HttpResponseRedirect(the_link.get_absolute_url())
            
@login_required
def save_link(request, link_id):        
    try:
        link = Link.objects.get(id = link_id)
        saved_link = SavedLink(user = request.user, link = link)
        saved_link.save()
        return HttpResponse(str(link.id))
    except IntegrityError :
        return HttpResponse(str(-1))
 

@login_required
def user_details_x(request, user_name = None):
    return user_details(request, user_name = None)
    
@login_required    
def saved_links_x(request, user_name = None):        
    return saved_links(request, user_name = None)

@login_required    
def liked_links_x(request, up, user_name = None, ):
    return liked_links(request, up, user_name = None, )    

@login_required
def submit_comment(request):
    class CommentForm(forms.Form):
        text = forms.CharField(widget=forms.Textarea)
    if request.method == 'GET':
        com_f = CommentForm()
        action = '.'
        method = 'post'
        #return wrap_form(com_f, action, method)
        return com_f
    elif request.method == 'POST':
        com_f = CommentForm(request.POST)
        action = '.'
        method = 'post'
        if com_f.is_valid():
            link_id = request.session['link_id']
            link = Link.objects.get(id = link_id)
            user = request.user
            text = request.POST['text']
            comment = Comment.objects.create_comment(link = link, user = user, text = text, )
            comment.save()
            #return wrap_form(com_f, action, method)            
            return com_f
        else:
            #return wrap_form(com_f, action, method)
            return com_f
@login_required      
def tag_link(request):
    print 'tag_form'
    class TagForm(forms.Form):
        tags = forms.CharField()
    if request.method == 'GET':
        tag_f = TagForm()
        return tag_f
    elif request.method == 'POST':
        tag_f = TagForm(request.POST)
        if tag_f.is_valid():
            link_id = request.session['link_id']
            link = Link.objects.get(id = link_id)
            user = request.user
            text = request.POST['tags']   
            tags_ = text.split(',')
            for tag_ in tags_:
                tag = Tags.objects.add_tag(user, link, tag_)         
            return tag_f
        else:
            return tag_f
        
        
        
def register(request):
    form = UserCreationForm()

    if request.method == 'POST':
        data = request.POST.copy()
        errors = form.get_validation_errors(data)
        if not errors:
            new_user = form.save(data)
            return HttpResponseRedirect("/accounts/profile/")
    else:
        data, errors = {}, {}

    return render_to_response("registration/register.html", {
        'form' : oldforms.FormWrapper(form, data, errors)
    })        

@login_required
def link_submitted(request):
    return HttpResponse('Your link submitted')



def test(request):
    """Request page"""
    entry = ({'title':'hello kitty', 'body':'bye kitty'},)
    Link.objects.update_points()
    return render_to_response('test.html', {'blog_entries':entry})

    

def wrap_form(form, action, method):
    start_form = '<form action="%s" method="%s">' % (action, method)
    end_form =   '<input type="submit" /></form>'
    return start_form + form.as_p() + end_form

def _populate_link_data(link, user):
      x = urlparse(link.link)
      link.domain = x[1]    
      link.num_comments = Comment.objects.filter(link = link).count()
      link.time_elapsed = _normalize_timedelta(link.added_on.now() - link.added_on)
      saved_links = SavedLink.objects.filter(link = link, user = user)
      link.saved = False
      for saved_link in saved_links:
          link.saved = True
      link.upvoted = False
      link.downvoted = False
      votes = UserVotes.objects.filter(link = link, user = user)       
      for vote in votes:
           link.upvoted = vote.upvote          
           link.downvoted = not vote.upvote          
      return link    

def _populate_links_data(links, user):
    for link in links:
       x = urlparse(link.link)
       link.domain = x[1]
       print link.domain
       link.num_comments = Comment.objects.filter(link = link).count()
       link.time_elapsed = _normalize_timedelta(link.added_on.now() - link.added_on)
       saved_links = SavedLink.objects.filter(link = link, user = user)
       link.saved = False
       for saved_link in saved_links:
          link.saved = True
       link.vote = None
       link.upvoted = False
       link.downvoted = False
       votes = UserVotes.objects.filter(link = link, user = user)       
       for vote in votes:
           link.upvoted = vote.upvote          
           link.downvoted = not vote.upvote         
    return links  

def _populate_comments_data(comments):
    for comment in comments:
       comment.time_elapsed = _normalize_timedelta(comment.added_on.now() - comment.added_on)
    return comments  

def _normalize_timedelta(timedel):
    if not timedel.days == 0:
        return '%s days' % timedel.days
    if not timedel.seconds/3600 == 0:
        return '%s hours' % (timedel.seconds/3600)
    
    if not timedel.seconds/60 == 0:
        return '%s minutes' % (timedel.seconds/60)
    if not timedel.seconds == 0:
        return '%s seconds' % timedel.seconds
    return '%s milliseconds' % (timedel.microseconds/1000)


"""
def all_comment(request):
    links = ''
    for link in Link.objects.all():
        links += str(link)
        links += '<br>'
        for comment in Comment.objects.filter(link = link.id):
            links += str(comment)
            links +='<br>'
        links +='<br>'
    return HttpResponse(links)    
"""
    
    
    
    
    
    
    
    
    
    