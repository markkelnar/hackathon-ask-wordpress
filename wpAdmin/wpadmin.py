# https://python-wordpress-xmlrpc.readthedocs.io/en/latest/overview.html

from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost, GetPost, EditPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc.methods.comments import GetCommentCount, GetCommentStatusList, GetComments

class WpAdmin:

    def __init__(self):
	user = 'alexa'
	pass = 'redacted'
        self.wp = Client('https://markkelnar.com/xmlrpc.php', user, pass)

    def getPosts(self):
        r = self.wp.call(GetPosts())
        drafts = []
        published = []
        for post in r:
            if 'draft' == post.post_status:
                drafts.append(post)
            else:
                published.append(post)
        return {'drafts':drafts, 'published':published}

    def getPostContent(self, post_id):
        post = self.wp.call(GetPost(post_id))
        return post.content

    def getCommentStatus(self):
        r = self.wp.call(GetCommentStatusList())
        filter = {'post_id': 347}
        r = self.wp.call(GetComments(filter=filter))
        return self

    def createPost(self, title, content):
        post = WordPressPost()
        post.title = title
        post.content = content
        # terms are categories
        post.terms_names = {
            'post_tag': ['test', 'firstpost'],
            'category': ['Introductions', 'Tests']
        }
        post_id = self.wp.call(NewPost(post))
        return post_id

    def publishPost(self, post_id):
        post = self.wp.call(GetPost(post_id))
        post.post_status = 'publish'
        self.wp.call(EditPost(post_id, post))
        return post_id

