from bulb.core.exceptions import BULBException, BULBWarning


#################
# ERROR CLASSES #
#################

#  BULBException--> BULBDatabaseError
class BULBDatabaseError(BULBException):
    pass


#  BULBException --> BULBDatabaseError --> BULBBaseNodeAndRelationshipError
class BULBBaseNodeAndRelationshipError(BULBDatabaseError):
    pass


#  BULBException --> BULBDatabaseError --> BULBBaseNodeAndRelationshipError --> BULBFakeInstanceError
class BULBFakeInstanceError(BULBBaseNodeAndRelationshipError):
    pass


#  BULBException --> BULBDatabaseError --> BULBNodeError
class BULBNodeError(BULBDatabaseError):
    pass


#  BULBException --> BULBDatabaseError --> BULBNodeError --> BULBLabelsError
class BULBLabelsError(BULBNodeError):
    pass


#  BULBException --> BULBDatabaseError --> BULBPropertyError
class BULBPropertyError(BULBDatabaseError):
    pass


#  BULBException --> BULBDatabaseError --> BULBPropertyError --> BULBRequiredConstraintError
class BULBRequiredConstraintError(BULBPropertyError):
    pass


#  BULBException --> BULBDatabaseError --> BULBPropertyError --> BULBUniqueConstraintError
class BULBUniqueConstraintError(BULBPropertyError):
    pass


#  BULBException --> BULBDatabaseError --> BULBRelationshipError
class BULBRelationshipError(BULBDatabaseError):
    pass


#  BULBException --> BULBDatabaseError --> BULBTransactionError
class BULBTransactionError(BULBDatabaseError):
    pass


#  BULBException --> BULBDatabaseError --> BULBSessionError
class BULBSessionError(BULBDatabaseError):
    pass


#  BULBException --> BULBDatabaseError --> BULBConnectionError
class BULBConnectionError(BULBDatabaseError):
    pass


###################
# WARNING CLASSES #
###################

#  BULBWarning --> BULBDatabaseWarning
class BULBDatabaseWarning(BULBWarning):
    pass


#  BULBWarning --> BULBDatabaseWarning --> BULBNodeWarning
class BULBNodeWarning(BULBDatabaseWarning):
    pass


#  BULBWarning --> BULBDatabaseWarning --> BULBRelationshipInstanceWarning
class BULBRelationshipInstanceWarning(BULBDatabaseWarning):
    pass


#  BULBWarning --> BULBDatabaseWarning --> BULBConnectionWarning
class BULBConnectionWarning(BULBDatabaseWarning):
    pass
