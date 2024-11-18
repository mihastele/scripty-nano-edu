class Environment:
    def __init__(self, parent=None):
        self.vars = {} # dictionary to store variables
        self.parent = parent  # reference to the parent environment

    def get_var(self, name):
        return self.vars.get(name, None)  # return None if variable not found in the environment

    def set_var(self, name, value):
        self.vars[name] = value

    def new_env(self):
        '''
        Create a new child environment
        '''
        return Environment(parent=self)  # create a new child environment