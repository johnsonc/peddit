from django.contrib.syndication.feeds import Feed
from reddit.models import Link, Comment
from django.contrib.auth.models import User

class Latest(Feed):
    title = "What's cookin"
    link = "/"
    description = "Updates on changes and additions to chicagocrime.org."

    def items(self):
        return Link.objects.all().order_by('-points', '-added_on')[:10]
    
class Detail(Feed):
    def get_object(self, bits):
        # In case of "/rss/beats/0613/foo/bar/baz/", or other such clutter,
        # check that bits has only one member.
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Link.objects.get(id = bits[0])   
     
    def title(self, obj):
        return "%s" % obj.get_absolute_url()

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return "%s" % obj.text

    def items(self, obj):
        return Comment.objects.filter(link__id__exact=obj.id)[:30] 
    

"""
Todo - not working
"""      
class User(Feed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return User.objects.get(username = bits[0])  
     
    def title(self, obj):
        return '1'
        #return "%s" % obj.username

    def link(self, obj):
        return '1'
        #return '/user/%s/' % obj.username

    def description(self, obj):
        return '1'
        #return "Links by %s's " % obj.username

    def items(self, obj):
        return Links.objects.all()[:30] 
