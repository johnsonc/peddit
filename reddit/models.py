from django.db import models
from django.db import connection
from django.contrib.auth.models import *
from django.utils.html import escape

class LinkManager(models.Manager):
    """Manager for class link"""
    def create_link(self, link, user, text):
        link = Link(link=link, user = user, text = escape(text), votes = 0)
        link.upvote(user)
        return link
    
    def update_points(self):
        cursor = connection.cursor()
        cursor.callproc('update_points')
        
class VotingManager(models.Manager):     
    """Manager for classs UserVotes"""  
    pass

class CommentManager(models.Manager):     
    """Manager for classs Comment"""  
    def create_comment(self, link, user, text):
        return Comment(link = link, user = user, text = escape(text), )
    

class TagsManager(models.Manager):     
    """Manager for classs UserVotes"""  
    def add_tag(self, user, link, tag):
        prev_tags = Tags.objects.filter(link = link, tag = tag)
        for prev_tag in prev_tags:
            prev_tag.tag_points += 1
            prev_tag.save()
            return prev_tag
        new_tag = Tags(user = user, link = link, tag = escape(tag))
        new_tag.save()
        return new_tag
            
         
         



class Link(models.Model):
    """Model for links stored"""
    link = models.URLField(unique = True)
    user = models.ForeignKey(User, unique=False)
    text = models.CharField(maxlength = 200)
    votes = models.IntegerField(default = 0)
    added_on = models.DateTimeField(auto_now_add = 1)
    objects = LinkManager()
    points = models.IntegerField(default = 0)
        
    def upvote(self, user):
        """Upvote this link. If user has already voted, return."""
        for user in UserVotes.objects.filter(link = self, user = user):
            
            if user.upvote == True:
                return False
            elif user.upvote == False:
                user.delete()
                user.save()        
        self.votes = self.votes + 1
        self.points = self.points + 1
        return True
        
    def downvote(self, user):
        """Downvote this link. If user has already downvoted, return."""
        for user in UserVotes.objects.filter(user = user, link = self):
            if user.upvote == False:
                return False  
            elif user.upvote == True:
                user.delete()
                user.save()
        self.votes = self.votes - 1
        self.points = self.points - 1
        return True
    
    def vote(self, user, dir):
        """dir = True, upvote. dir = False, downvote"""
        for user in UserVotes.objects.filter(user = user, link = self):
            #There is a uservote with this link
            if user.upvote == dir:
                return False
            user.upvote = dir
            user.save()
            def change_points(dir):
                if dir == True:
                    return 2
                return -2
            self.votes = self.votes + change_points(dir)
            self.points = self.points + change_points(dir)
            self.save()
            return True
        vote = UserVotes(user = user, link = self, upvote = dir)
        vote.save()
        def change_points(dir):
           if dir == True:
                    return 1
           return -1
        self.votes = self.votes + change_points(dir)
        self.points = self.points + change_points(dir)
        self.save()
        return True
        
        
    
    def get_absolute_url(self):
        return '/details/%i/'%self.id
        
    def __str__(self):
        return str(self.link)
    
    class Admin:
        pass
    
    class Meta:
        ordering = ['-points', '-added_on']
        
class SavedLink(models.Model):
    """The links a user saved"""
    user = models.ForeignKey(User, unique = False)
    link = models.ForeignKey(Link, unique = False)
    added_on = models.DateTimeField(auto_now_add = 1)
    
    def __str__(self):
        return '%s:%s' % (self.user.username, self.link.link)
    
    class admin:
        pass
    
    class Meta:
        unique_together = (('user', 'link'),)
        
class Tags(models.Model):        
    user = models.ForeignKey(User, unique = False) #First user who tagged this tag.
    link = models.ForeignKey(Link, unique = False)
    tag = models.TextField(maxlength = 30)
    tag_points = models.IntegerField(default = 1) #How many users tagged with this tag.
    objects = TagsManager()
        
    def __str__(self):
        return str(self.tag)
    
    class Admin:
        pass
    
    class Meta:
        pass
        #unique_together = (('link', 'tag'),)
        
    def get_absolute_url(self):
        return '/tags/%s/'%self.tag      

class Comment(models.Model):
    """Comments left by the user"""
    link = models.ForeignKey(Link, unique=False)
    user = models.ForeignKey(User, unique = False)
    text = models.CharField(maxlength = 2000)
    votes = models.IntegerField(default = 0)
    added_on = models.DateTimeField(auto_now_add = 1)
    objects = CommentManager()
        
    def upvote(self):
        votes = votes + 1
        
    def downvote(self):
        votes = votes - 1
        
    def __str__(self):
        return str(self.text)
    
    def get_absolute_url(self):
        return '/comment/%i/'%self.id    
    
    class Admin:
        pass    
    
class UserVotes(models.Model):
    """The links a specific user voted on."""    
    user = models.ForeignKey(User, unique = False)
    link = models.ForeignKey(Link, unique = False)
    upvote = models.BooleanField(default = True)
    
    objects = VotingManager()
    
    class Admin:
        pass
    
    def __str__(self):
        return 'user: %s, site: %s' % (self.user.username, self.link.link)
    
    class Meta:
        unique_together = (('user', 'link'),)
    
class CommentVote(models.Model):   
    """The comments a specific user voted on""" 
    user = models.ForeignKey(User, unique = False)
    comment = models.ForeignKey(Comment, unique = False)
    upvote = models.BooleanField(default = True)
    
    def __str__(self):
        'user: %s, site: %s' % (self.user.username, self.comment.text)
    
    class Admin:
        pass
    
    class Meta:
        unique_together = (('user', 'comment'),)        
    
      
    
class UserProfile(models.Model):    
    """Profile data for users."""
    user = models.ForeignKey(User, unique = True, default=0)
    karma = models.IntegerField()
    page_links = models.IntegerField()
    
    def get_absolute_url(self):
        return '/user/%s/'%user.username
    
    def __str__(self):
        return "%s's profile"%user.username
    
    
    
    