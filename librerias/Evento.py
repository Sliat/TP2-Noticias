
# The actual Event class
class Evento(object):
    def __init__(self, action, args=(), kwargs={}):
        self.action = action
        self.args = args
        self.kwargs = kwargs

    def iniciar(self):
        #self.action(*self.args, **self.kwargs)
        self.action()
