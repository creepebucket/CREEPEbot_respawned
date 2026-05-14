from lib.chat.rule import Rule


class Command(Rule):

    def __init__(self, id: str, name: str, desc: str, usage: str, priority: int = 0, bypass_enable_check: bool = False):
        super().__init__(name, desc, usage, priority, bypass_enable_check)
        self.id = id
