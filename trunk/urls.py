from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
from reddit.feeds import Latest, Detail, User

feeds = {
    'latest': Latest,
    'details': Detail,
    'user' : User,
}

urlpatterns = patterns('reddit.views',
    (r'^$','index'),
    (r'^submit/$','submit_link'),
    (r'^submitted/$','link_submitted'),
    (r'^comment/$','submit_comment'),
    (r'^details/(?P<link_id>\d+)/$','show_details'),
    (r'^comment/(?P<comment_id>\d+)/$','show_comment'),
    (r'^save/(?P<link_id>\d+)/$','save_link'),
    (r'^upvote/(?P<link_id>\d+)/$','vote_link', {'up':True}),
    (r'^downvote/(?P<link_id>\d+)/$','vote_link', {'up':False}),
    (r'^user/(?P<user_name>\w+)/$','user_details'),
    (r'^tags/(?P<tag_text>\w+)/$','show_tagged_links'),
    (r'^user/(?P<user_name>\w+)/saved/$','saved_links'),
    (r'^user/(?P<user_name>\w+)/liked/$', 'liked_links', {'up':True}),
    (r'^user/(?P<user_name>\w+)/disliked/$', 'liked_links', {'up':False}),
    (r'^user/(?P<user_name>\w+)/comments/$','user_comments'),    
    (r'^accounts/profile/$','user_details'),
    (r'^accounts/profile/saved/$','saved_links'),
    (r'^accounts/profile/liked/$','liked_links', {'up':True}),
    (r'^accounts/profile/disliked/$','liked_links', {'up':False}),
    (r'^accounts/profile/comments/$','user_comments', ),
    (r'^test/$','test'),        
    (r'^register/$','register'), 
    (r'^accounts/$','index'),    #Todo 
    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
  
)

urlpatterns += patterns('',
    (r'^accounts/login/$',  login, {'template_name': 'registration/login.html'}),
    (r'^accounts/logout/$', logout),                  
                )

urlpatterns += patterns('',
        (r'^foo/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'C:/django/redpy/templates/media'}),
        (r'^js/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'C:/django/redpy/templates/js'}),
    )

#feeds
urlpatterns += patterns('',
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    )
