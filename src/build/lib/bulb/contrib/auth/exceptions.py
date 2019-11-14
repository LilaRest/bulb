class BULBPermissionDoesNotExist(Exception):
    pass


class BULBGroupDoesNotExist(Exception):
    pass


class BULBUserWarning(Warning):  # Useful
    pass


class BULBAnonymousUserWarning(Warning):  # Useful
    pass


class BULBPermissionWarning(Warning):  # Useful
    pass


class BULBGroupWarning(Warning):  # Useful
    pass


class BULBUserPropertyWarning(Warning):
    pass


class BULBPermissionPropertyWarning(Warning):
    pass


class BULBGroupPropertyWarning(Warning):
    pass


class BULBGetUserError(Exception):
    pass


class BULBGetGroupError(Exception):
    pass


class BULBGetPermissionError(Exception):
    pass


class BULBLoginError(Exception):
    pass

