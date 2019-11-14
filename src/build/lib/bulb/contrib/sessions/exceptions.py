from bulb.db.exceptions import BULBNodeError


class BULBSessionError(Exception):
    pass


class BULBSessionWarning(Warning):
    pass


class BULBSessionDoesNotExist(BULBNodeError):
    pass


class BULBSessionDoesNotHaveData(BULBNodeError):
    pass
