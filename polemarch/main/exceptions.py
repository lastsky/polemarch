class PMException(Exception):
    def __init__(self, *args, **kwargs):
        self.msg = (list(args)[0:1]+[""])[0]
        super(PMException, self).__init__(*args, **kwargs)

    def __repr__(self):
        return repr(self.msg)


class UnknownModelHandlerException(PMException):
    _def_message = "Unknown type {}."

    def __init__(self, tp):
        msg = self._def_message.format(tp)
        super(UnknownModelHandlerException, self).__init__(msg)


class NodeFailedException(PMException):
    pass


class NodeOfflineException(PMException):
    pass


class AnsibleNotFoundException(PMException):
    pass
