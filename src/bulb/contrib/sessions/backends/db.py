from bulb.contrib.sessions.exceptions import BULBSessionDoesNotExist
from django.contrib.sessions.backends.base import CreateError, SessionBase
from django.core.exceptions import SuspiciousOperation
from django.utils.functional import cached_property
import logging


class SessionStore(SessionBase):
    """
    Implement database session store.
    """
    def __init__(self, session_key=None):
        super().__init__(session_key)

    @classmethod
    def get_model_class(cls):
        # Avoids a circular import and allows importing SessionStore when
        # django.contrib.sessions is not in INSTALLED_APPS.
        from bulb.contrib.sessions.node_models import Session
        return Session

    @cached_property
    def model(self):
        return self.get_model_class()

    def _get_session_from_db(self):
        session = self.model.get(session_key=self.session_key)

        if session is not None:
            return session

        else:
            # if isinstance(e, SuspiciousOperation):
            #     logger = logging.getLogger('django.security.%s' % e.__class__.__name__)
            #     logger.warning(str(e))
            self._session_key = None

        # try:
        #     return self.model.get(session_key=self.session_key)
        #
        # except (BULBSessionDoesNotExist, SuspiciousOperation) as e:
        #     if isinstance(e, SuspiciousOperation):
        #         logger = logging.getLogger('django.security.%s' % e.__class__.__name__)
        #         logger.warning(str(e))
        #     self._session_key = None

    def load(self):
        s = self._get_session_from_db()

        if s is not None:
            session_data = s.session_data
            return self.decode(session_data)

        else:
            return {}

    def exists(self, session_key):
        return self.model.exists(session_key=session_key)

    def create(self):
        while True:
            self._session_key = self._get_new_session_key()
            try:
                # Save immediately to ensure we have a unique entry in the
                # database.
                self.save(must_create=True)

            except CreateError:
                # Key wasn't unique. Try again.
                continue
            self.modified = True
            return

    # def create_model_instance(self, data):
    #     """
    #     Return a new instance of the session model object, which represents the
    #     current session state. Intended to be used for saving the session data
    #     to the database.
    #     """
    #     return self.model(
    #         session_key=self._get_or_create_session_key(),
    #         session_dict=self.encode(data),
    #         expire_date=self.get_expiry_date(),
    #     )

    def save(self, must_create=False):
        """
        Save the current session data to the database. If 'must_create' is
        True, raise a database error if the saving operation doesn't create a
        new entry (as opposed to possibly updating an existing entry).
        """
        if self.session_key is None:
            return self.create()

        data = self._get_session(no_load=must_create)

        if not self._get_session_from_db():
            obj = self.model(session_key=self._get_or_create_session_key(),
                             session_data=self.encode(data),
                             expire_date=self.get_expiry_date())

            return obj

    def delete(self, session_key=None):
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        try:
            self.model.delete_session(session_key=session_key)
        except BULBSessionDoesNotExist:
            pass

    @classmethod
    def clear_expired(cls):
        cls.get_model_class().clear_expired_sessions()
