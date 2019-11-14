
# Base bulb error
class bulbError(BaseException):
    pass


#  Base bulb error --> Client error
class BULBClientError(bulbError):
    pass


#  Base bulb error --> Client error --> Node error
class BULBNodeError(BULBClientError):
    pass

class BULBNodeWarning(Warning):
    pass

#  Base bulb error --> Client error --> Node error --> Node initialization error --> labels
class BULBNodeLabelsInitializationError(BULBNodeError):
    pass


# Base bulb error --> Client error --> Connection error
class BULBConnectionError(BULBClientError):
    pass


# Base bulb error --> Client error --> Connection warning
class BULBConnectionWarning(BULBClientError, Warning):
    pass


# Base bulb error --> Client error --> Transaction error
class BULBTransactionError(BULBClientError):
    pass


# Base bulb error --> Client error --> Transaction error --> Transaction type error
class BULBTransactionTypeError(BULBTransactionError):
    pass


# Base bulb error --> Client error --> Transaction error --> Transaction conflict error
class BULBTransactionConflictError(BULBTransactionError):
    pass


# Base bulb error --> Client error --> Session error
class BULBSessionError(BULBClientError):
    pass


#  Base bulb error --> Database error
class BULBDatabaseError(bulbError):
    pass


#  Base bulb error --> Database error --> field error
class BULBFieldError(BULBDatabaseError):
    pass


#  Base bulb error --> Database error --> field error --> required constraint error
class BULBRequiredConstraintError(BULBFieldError):
    pass


#  Base bulb error --> Database error --> unique constraint error
class BULBUniqueConstraintError(BULBFieldError):
    pass


#  Base bulb error --> Database error --> attribute error
class BULBAttributeError(BULBFieldError):
    pass


class BULBFileError(Exception):
    pass


class BULBRelationshipError(Exception):  # verified
    pass


class BULBRelationshipInstanceWarning(Warning):  # verified
    pass


class BULBBaseNodeAndRelationshipError(Exception):  # verified
    pass
