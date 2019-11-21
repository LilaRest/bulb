from bulb.core.exceptions import BULBException, BULBWarning


#################
# ERROR CLASSES #
#################

#  BULBException --> BULBSessionError
class BULBSessionError(BULBException):
    pass

#  BULBException --> BULBSessionError --> BULBSessionDoesNotExist
class BULBSessionDoesNotExist(BULBSessionError):
    pass

#  BULBException --> BULBSessionError --> BULBSessionDoesNotHaveData
class BULBSessionDoesNotHaveData(BULBSessionError):
    pass


###################
# WARNING CLASSES #
###################

#  BULBWarning --> BULBSessionWarning
class BULBSessionWarning(BULBWarning):
    pass
