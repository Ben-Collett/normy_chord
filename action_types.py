class Action:
    def __init__(self, conditionals=[]):
        self.conditionals = conditionals


class WriteAction(Action):
    def __init__(self, data, conditionals=[]):
        self.data = data
        super().__init__(conditionals)


class TypeAction(Action):
    def __init__(self, key_codes, conditionals=[]):
        self.key_codes = key_codes
        super().__init__(conditionals)


class ActionList:
    def __init__(self):
        self.actions = []

    def and_then(self, action):
        if isinstance(action, ActionList):
            self.actions.extend(action.actions)
        else:
            self.actions.append(action)
        return self

    def __iter__(self):
        return iter(self.actions)
