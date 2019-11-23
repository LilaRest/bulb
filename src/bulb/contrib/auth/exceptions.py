from bulb.core.exceptions import BULBException, BULBWarning


#################
# ERROR CLASSES #
#################

#  BULBException --> BULBAuthError
class BULBAuthError(BULBException):
    pass


#  BULBException --> BULBAuthError --> BULBPermissionError
class BULBPermissionError(BULBAuthError):
    pass


#  BULBException --> BULBAuthError --> BULBLoginError
class BULBLoginError(BULBAuthError):
    pass


###################
# WARNING CLASSES #
###################

#  BULBException --> BULBAuthWarning
class BULBAuthWarning(BULBWarning):
    pass


#  BULBException --> BULBAuthWarning --> BULBAuthNodeModelsWarning
class BULBAuthNodeModelsWarning(BULBAuthWarning):
    pass
