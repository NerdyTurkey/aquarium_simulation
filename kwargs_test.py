DEFAULT_PARAMS = {"a": 10, "b": 20}


class C:
    def __init__(self, **kwargs):
        params = DEFAULT_PARAMS.copy()
        filtered_params = {k: v for k, v in kwargs.items() if v is not None}
        params.update(filtered_params)
        self.__dict__.update(params)
        print(self.__dict__)
        print(self.a, self.b)


params = {"a": 100}
c = C(**params)
