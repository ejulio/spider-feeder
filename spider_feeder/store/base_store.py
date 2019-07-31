class BaseStore:

    def __init__(self, settings):
        self._input_field = settings.get('SPIDERFEEDER_INPUT_FIELD')

    def __iter__(self):
        for item in self.read_input_items():
            if self._input_field:
                if not isinstance(item, dict):
                    raise TypeError('Data is expected to be a dict when SPIDERFEEDER_INPUT_FIELD is set.')  # noqa

                yield (item[self._input_field], item)
            else:
                yield (item, {})

    def read_input_items(self):
        raise NotImplementedError()
