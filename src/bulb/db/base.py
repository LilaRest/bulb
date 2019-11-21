from bulb.utils.log import bulb_logger
from neo4j.v1 import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
from bulb.db.exceptions import *
from django.conf import settings
import warnings
import time


class Database:
    """
    This class deserves connection and disconnection between a Neo4j database and a Django project, and their
    parameters.

    :param (optional) uri: The Neo4j database uri ('bolt' or 'bolt+routing')
                           Explanations here :
                           https://neo4j.com/docs/driver-manual/1.7/client-applications/#driver-connection-uris

    :param (optional) id: The Neo4j database user's id / username.

    :param (optional) password: The Neo4j database user's password.

    :param (optional) encrypted: Encrypting traffic between the Neo4j driver and the Neo4j instance.
                                 Explanations here :
                                 https://neo4j.com/docs/developer-manual/3.0/drivers/driver/#driver-authentication-encryption

    :param (optional) trust: Verification against "man-in-the-middle" attack.
                             Explanations : https://neo4j.com/docs/developer-manual/3.0/drivers/driver/#_trust
                             Choices :
                             0 : TRUST_ON_FIRST_USE     (Deprecated)
                             1 : TRUST_SIGNED_CERTIFICATES     (Deprecated)
                             2 : TRUST_ALL_CERTIFICATES
                             3 : TRUST_CUSTOM_CA_SIGNED_CERTIFICATES
                             4 : TRUST_SYSTEM_CA_SIGNED_CERTIFICATES
                             5 : TRUST_DEFAULT = TRUST_ALL_CERTIFICATES

    These parameters define the transactions modalities (after the establishment of the initial connection)
    Explanations here : https://neo4j.com/docs/api/python-driver/current/driver.html#max-connection-lifetime
        :param (optional) max_connection_lifetime:
        :param (optional) max_connection_pool_size:
        :param (optional) connection_acquisition_timeout:
        :param (optional) connection_timeout:
        :param (optional) max_retry_time:
    """

    def __init__(self,
                 uri=settings.BULB_DATABASE_URI,
                 id=settings.BULB_DATABASE_ID,
                 password=settings.BULB_DATABASE_PASSWORD,
                 encrypted=settings.BULB_DATABASE_ENCRYPTED,
                 trust=settings.BULB_DATABASE_TRUST,
                 max_connection_lifetime=settings.BULB_DATABASE_MAX_CONNECTION_LIFETIME,
                 max_connection_pool_size=settings.BULB_DATABASE_MAX_CONNECTION_POOL_SIZE,
                 connection_acquisition_timeout=settings.BULB_DATABASE_CONNECTION_ACQUISITION,
                 connection_timeout=settings.BULB_DATABASE_CONNECTION_TIMEOUT,
                 max_retry_time=settings.BULB_DATABASE_MAX_RETRY_TIME):
        self.uri = uri
        self.id = id
        self.password = password
        self.encrypted = encrypted
        self.trust = trust
        self.max_connection_lifetime = max_connection_lifetime
        self.max_connection_pool_size = max_connection_pool_size
        self.connection_acquisition_timeout = connection_acquisition_timeout
        self.connection_timeout = connection_timeout
        self.max_retry_time = max_retry_time

        self.initial_connection_attempts_number = settings.BULB_INITIAL_CONNECTION_ATTEMPTS_NUMBER
        self.driver = None

    def open_connection(self):
        """
        This method tries to establish a connection with the Neo4j database, considering the parameters in the settings.py
        file in a first time (with the _try_connection() method), then, using default ones (with the
        _try_default_connection() method).
        """
        connection_attempts = 0
        response_connection = False
        response_default_connection = False

        while True:
            connection_attempts = connection_attempts + 1
            response_connection = self._try_connection()

            if connection_attempts >= self.initial_connection_attempts_number:
                bulb_logger.error(
                '''BULBConnectionError("""
                The connection with the Neo4j database cannot be established, please check if :
                - your database is still running,
                - yours authentication credentials (uri, id, password) are valid in the settings.py file of your project.
                """)''')
                raise BULBConnectionError("""
                The connection with the Neo4j database cannot be established, please check if :
                - your database is still running,
                - yours authentication credentials (uri, id, password) are valid in the settings.py file of your project.
                """)

            else:
                response_default_connection = self._try_default_connection()

            if response_connection or response_default_connection:
                break

            time.sleep(1)

    def _try_connection(self):
        """
        :return True: if the connection has been established.
        :return False: if the connection hasn't been established.
        """
        try:
            self.driver = GraphDatabase.driver(uri=self.uri,
                                               auth=(self.id, self.password),
                                               encrypted=self.encrypted,
                                               trust=self.trust,
                                               max_connection_lifetime=self.max_connection_lifetime,
                                               max_connection_pool_size=self.max_connection_pool_size,
                                               connection_acquisition_timeout=self.connection_acquisition_timeout,
                                               connection_timeout=self.connection_timeout,
                                               max_retry_time=self.max_retry_time)

        except (ServiceUnavailable, AuthError):
            return False
        else:
            return True

    def _try_default_connection(self):
        """
        :return True: if the connection has been established.
        :return False: if the connection hasn't been established.
        """

        try:
            self.driver = GraphDatabase.driver(uri="bolt://localhost:7687",
                                               auth=("neo4j", "neo4j"),
                                               encrypted=self.encrypted,
                                               max_connection_lifetime=self.max_connection_lifetime,
                                               max_connection_pool_size=self.max_connection_pool_size,
                                               connection_acquisition_timeout=self.connection_acquisition_timeout,
                                               connection_timeout=self.connection_timeout,
                                               max_retry_time=self.max_retry_time)

        except (ServiceUnavailable, AuthError):
            return False

        else:
            bulb_logger.warning(
                'BULBConnectionWarning("WARNING : Yours database informations are not valid, the connection has been establish with the default authentification informations (uri = \'bolt://localhost:7687\', id = \'neo4j\', password = \'neo4j\'."')
            warnings.warn(
                "Yours database informations are not valid, the connection has been establishwith the default authentification informations (uri = 'bolt://localhost:7687', id = 'neo4j', password = 'neo4j'.",
                BULBConnectionWarning)
            return True

    def close_connection(self):
        """
        This method ends the database connection.
        """
        self.driver.close()


class Session:
    """
    This class creates a Neo4j session and handle its behaviours.
    You can learn more here : https://neo4j.com/docs/driver-manual/1.7/sessions-transactions/#driver-sessions
    :param (required) database_instance  : An instance of the above Database class.
    :param (optional) type  : The type of the session ('WRITE' or 'READ'). This type can be overridden by the type of
                              each transaction in the session.
                              Explanations here :
                              https://neo4j.com/docs/driver-manual/1.7/sessions-transactions/#driver-transactions-access-mode
    :param (optional) bookmarks : The bookmark in a Neo4j causal chaining.
                                  Explanation here:
                                  https://neo4j.com/docs/driver-manual/1.7/sessions-transactions/#driver-transactions-causal-chaining
    """
    def __init__(self, database_instance, type=None, bookmarks=None):
        self.database_instance = database_instance
        self.type = Session.check_and_set_session_type(type)
        self.session = None
        self.bookmarks = bookmarks

    def __enter__(self):
        try:
            self.session = self.database_instance.driver.session(access_mode=self.type, bookmark=self.bookmarks)
        except AttributeError:
            bulb_logger.error(
                'BULBConnectionError("Failed to establish connection with the database. Check yours given informations (uri, id and password).")')
            raise BULBConnectionError(
                "Failed to establish connection with the database. Check yours given informations (uri, id and password).")
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Ensure that the session is closed
        self.session.close()

    @staticmethod
    def check_and_set_session_type(session_type):
        if session_type not in ['WRITE', 'READ', None]:
            bulb_logger.error(
                'BULBSessionError("The current session\'s type must be defined on \'WRITE\', \'READ\' or None.")')
            raise BULBSessionError("The current session's type must be defined on 'WRITE', 'READ' or None.")
        else:
            return session_type


class Transaction:
    """
    This class creates a Neo4j session and handle its behaviours.
    You can learn more here : https://neo4j.com/docs/driver-manual/1.7/sessions-transactions/#driver-sessions
    :param (required) session : An instance of the above Session class.
    :param (required) type : The type of the transaction ('WRITE' or 'READ'). This type, if filled, override the
                             type of session where is contained the transaction.
                             Explanations here :
                             https://neo4j.com/docs/driver-manual/1.7/sessions-transactions/#driver-transactions-access-mode
    :param (required) cypher_query : The cypher query to send to the Neo4j database.
    """
    def __init__(self, session, type, cypher_query):
        self.session = session
        self.type = Transaction.check_and_set_transaction_type(type)
        self.cypher_query = cypher_query

        self.active_transaction = None

    def __enter__(self):
        if self.active_transaction is None:
            if self.type == 'WRITE':
                self.active_transaction = self.session.write_transaction(
                    lambda tx, cypher_query: tx.run(cypher_query), self.cypher_query)
                return self.active_transaction.data()
            else:
                self.active_transaction = self.session.read_transaction(
                    lambda tx, cypher_query: tx.run(cypher_query), self.cypher_query)
                return self.active_transaction.data()
        else:
            bulb_logger.error('BULBTransactionError("A transaction is already running...")')
            raise BULBTransactionError("A transaction is already running...")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.active_transaction = None

    @staticmethod
    def check_and_set_transaction_type(transaction_type):
        if transaction_type not in ['WRITE', 'READ']:
            bulb_logger.error(
                f'BULBTransactionError("The current transaction\'s \'type\' must be defined on \'WRITE\', \'READ\' or None, not \'{transaction_type}\'.")')
            raise BULBTransactionError(
                f"The current transaction's 'type' must be defined on 'WRITE', 'READ' or None, not '{transaction_type}'.")
        else:
            return transaction_type


class GraphDatabaseHandler:
    """
    This class handles interactions between instances of the three above classes.
    Below, an instance of this class was created. This instance will have to be used in all the project to interact with
    the Neo4j database. (except in the case of a cluster)
    """
    def __init__(self):
        self.database_instance = Database()
        self.database_instance.open_connection()

    def get_database_instance(self):
        return self.database_instance

    def init_session(self, type=None, bookmarks=None):
        """
        This method creates and return a Session instance.

        :param (optional) type: The type of the session ('WRITE' or 'READ')
        :param (optional) bookmarks: The bookmarks recovered by the session.
        """
        return Session(database_instance=self.database_instance, type=type, bookmarks=bookmarks)

    def init_transaction(self, session, type, cypher_query):
        """
        This method creates and return a Transaction instance.

        :param (required) session: The session instance where is contained the transaction.
        :param (required) type: The type of the session.
        :param (required) cypher_query: The cypher query to send to the Neo4j database.
        """
        return Transaction(session=session, type=type, cypher_query=cypher_query)

    def w_transaction(self, cypher_query):
        """
        This method pre-configures and executes a writing transaction.
        :param cypher_query: The cypher query to send to the Neo4j database.
        :return: The response of the database.
        """
        with self.init_session('WRITE') as writing_session:
            with self.init_transaction(writing_session, 'WRITE', cypher_query) as writing_transaction:
                return writing_transaction

    def r_transaction(self, cypher_query):
        """
        This method pre-configures and executes a reading transaction.
        :param cypher_query: The cypher query to send to the Neo4j database.
        :return: The response of the database.
        """
        with self.init_session('READ') as reading_session:
            with self.init_transaction(reading_session, 'READ', cypher_query) as reading_transaction:
                return reading_transaction


gdbh = GraphDatabaseHandler()
