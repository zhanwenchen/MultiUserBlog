from handlers.BlogHandler import BlogHandler

class LogoutHandler(BlogHandler):

    def get(self):
        self.logout()
        self.redirect('/')
