
class Action:
    pass


class WriteAction(Action):
    def __init__(self, data):
        self.data


class TypeAction(Action):
    def __init__(self, key_codes):
        self.key_codes = key_codes


class ActionList:
    def __init__(self):
        self.actions = []

    def and_then(self, action):
        if action is ActionList:
            self.actions.extend(action.actions)
        else:
            self.actions.append(action)
        return self

    def __iter__(self):
        return iter(self.actions)
