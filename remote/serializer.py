class ModelSerializer(object):
    model_class = None
    __instance = None
    __many = None

    def __init__(self, model_class, instance=None, data=None, many=None):
        self.model_class = model_class
        self.__instance = instance
        self.__many = many
        if data:
            self.loads(data=data)

    def loads(self, data):
        if not self.__instance:
            if self.__many:
                self.__instance = []
            else:
                self.__instance = self.model_class()

        if self.__many:
            for entry, instance in zip(data, self.__instance):
                instance.__dict__.update(entry)
            if len(data) > len(self.__instance):
                for entry in data[len(self.__instance):]:
                    instance = self.model_class()
                    instance.__dict__.update(entry)
                    self.__instance.append(instance)
        else:
            self.__instance.__dict__.update(data)

    def get_instance(self):
        return self.__instance

    def get_dict(self):
        if self.__many:
            return [dict(entry.__dict__) for entry in self.__instance]
        else:
            return dict(self.__instance.__dict__)
