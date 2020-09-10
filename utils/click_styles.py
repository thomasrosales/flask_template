import click


class AbstractStyle:
    type_action = None
    color = None

    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return click.style(f'[{self.type_action.upper()}]', fg=f'{self.color}') + f' {self.message}'


class Created(AbstractStyle):
    type_action = 'created'
    color = 'green'


class Initialized(AbstractStyle):
    type_action = 'initiliazed'
    color = 'green'


class Dropped(AbstractStyle):
    type_action = 'dropped'
    color = 'yellow'


class Aborted(AbstractStyle):
    type_action = 'aborted'
    color = 'red'
