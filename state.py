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
        original_env = self  # save the current environment
        while self:
            if name in self.vars:
                self.vars[name] = value  # update the value in the current environment
                return value
            self = self.parent  # move up to the parent environment
        original_env.vars[name] = value
        return value  # return the updated value if the variable is not found in any environment

    def new_env(self):
        '''
        Create a new child environment
        '''
        return Environment(parent=self)  # create a new child environment