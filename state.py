class Environment:
    def __init__(self, parent=None):
        self.vars = {} # dictionary to store variables
        self.parent = parent  # reference to the parent environment

    def get_var(self, name):
        while self:
            value = self.vars.get(name)  # get the value of the variable from the current environment
            if value is not None:
                return value  # return the value if found
            else:
                self = self.parent  # move up to the parent environment
        return None  # return None if the variable is not found in any environment

    def set_var(self, name, value):
        self.vars[name] = value

    def new_env(self):
        '''
        Create a new child environment
        '''
        return Environment(parent=self)  # create a new child environment