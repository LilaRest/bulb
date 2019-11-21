from bulb.core.exceptions import BULBException, BULBWarning


#################
# ERROR CLASSES #
#################

#  BULBException --> BULBStaticfilesError
class BULBStaticfilesError(BULBException):
    pass


#  BULBException --> BULBSftpError
class BULBSftpError(BULBException):
    pass
