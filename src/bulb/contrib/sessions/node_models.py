from bulb.contrib.sessions.exceptions import BULBSessionError, BULBSessionDoesNotExist,\
    BULBSessionDoesNotHaveData, BULBSessionWarning
from bulb.utils.log import bulb_logger
from bulb.db import node_models
from bulb.db.base import gdbh
from django.utils import timezone
from django.conf import settings
import importlib.util
import warnings


class RelatedUserRelationship(node_models.Relationship):
    rel_type = "IS_SESSION_OF"
    direction = "from"
    start = "self"
    target = "User"
    auto = False
    on_delete = "PROTECT"
    unique = True


class AbstractBaseSession:

    def encode(self, session_dict):
        """
        Return the given session dictionary serialized and encoded as a string.
        """
        session_store_class = self.__class__.get_session_store_class()
        return session_store_class().encode(session_dict)

    def save(self, session_key, session_dict, expire_date):
        if session_dict:
            s = self.__class__(session_key, self.encode(session_dict), expire_date)
        else:
            bulb_logger.error(
                'BULBSessionDoesNotHaveData("The does\'nt have datas (\'session_dict\'), failed to save it.")')
            raise BULBSessionDoesNotHaveData("The does'nt have datas ('session_dict'), failed to save it.")
        return s

    def __str__(self):
        return self.session_key

    @classmethod
    def get_session_store_class(cls):
        bulb_logger.error('NotImplementedError')
        raise NotImplementedError

    def get_decoded(self):
        session_store_class = self.get_session_store_class()
        return session_store_class().decode(self.session_data)


class Session(node_models.Node, AbstractBaseSession):
    """
    Django provides full support for anonymous sessions. The session
    framework lets you store and retrieve arbitrary data on a
    per-site-visitor basis. It stores data on the server side and
    abstracts the sending and receiving of cookies. Cookies contain a
    session ID -- not the data itself.

    The Django sessions framework is entirely cookie-based. It does
    not fall back to putting session IDs in URLs. This is an intentional
    design decision. Not only does that behavior make URLs ugly, it makes
    your site vulnerable to session-ID theft via the "Referer" header.

    For complete documentation on using Sessions in your code, consult
    the sessions documentation that is shipped with Django (also available
    on the Django Web site).
    """

    session_key = node_models.Property(required=True,
                                       unique=True)  # TODO : add max_length = 40

    session_data = node_models.Property()

    expire_date = node_models.Property()  # TODO : add db_index = True

    related_user = RelatedUserRelationship()

    def __str__(self):
        return f'<Session object(session_key="{self.session_key}", expire_date="{str(self.expire_date)}")>'

    def __repr__(self):
        return f'<Session object(session_key="{self.session_key}", expire_date="{str(self.expire_date)}")>'

    @classmethod
    def get_session_store_class(cls):
        from bulb.contrib.sessions.backends.db import SessionStore
        return SessionStore

    @classmethod
    def get(cls, uuid=None, session_key=None, order_by=None, limit=None, skip=None, desc=False, only=None, filter=None,
            return_query=False):
        """
        This method allow the retrieving of Session (or of one of its children classes) instances.


        :param uuid: The Universal Unique Identifier of a session to get an unique session instance.

        :param session_key: The session_key of a session to get an unique session instance.

        :param order_by: Must be the name of the property with which the returned datas will be sorted.
                         Examples : "datetime", "first_name", etc...

        :param limit: Must be an integer. This parameter defines the number of returned elements.

        :param skip: Must be an integer. This parameter defines the number of skipped elements. For example if
                     self.skip = 3, the 3 first returned elements will be skipped.

        :param desc: Must be a boolean. If it is False the elements will be returned in an increasing order, but it is
                     True, they will be returned in a descending order.

        :param only: Must be a list of field_names. If this parameter is filled, the return will not be Permission
                     instances, but a dict with "only" the mentioned fields.

        :param filter: Must be Q statement. You must use the Q class stored in bulb.db
               Example: Q(name__contains="al") | Q(age__year__lte=8)

        :param return_query: Must be a boolean. If true, the method will return the cypher query.

        :return: If uuid is None, a list will be returned. Else it will be a unique instance.
        """
        where_statement = ""
        property_statement = ""
        order_by_statement = ""
        limit_statement = ""
        skip_statement = ""
        desc_statement = ""

        # Build the property_statement.
        if uuid is not None and session_key is not None:
            property_statement = "{uuid:'%s', session_key:'%s'}" % (uuid, session_key)

        elif uuid is not None:
            property_statement = "{uuid:'%s'}" % uuid

        elif session_key is not None:
            property_statement = "{session_key:'%s'}" % session_key

        # Build the match_statement.
        cyher_labels = node_models.DatabaseNode.format_labels_to_cypher(cls._get_labels())
        match_statement = f"MATCH (s:{cyher_labels} {property_statement})"

        # Build the where statement.
        if filter is not None:
            where_statement = "WHERE " + filter
            where_statement = where_statement.replace("n.", "s.")

        # Build the with_statement.
        with_statement = "WITH s"

        # Build order_by statements.
        if order_by is not None:
            order_by_statement = f"ORDER BY s.{order_by}"

        # Build return_statement statements.
        if not only:
            return_statement = "RETURN (s)"

        else:
            only_statement_list = []

            for element in only:
                only_statement_list.append(f"s.{element}")

            only_statement = ", ".join(only_statement_list)

            return_statement = f"RETURN {only_statement}"

        # Build limit_statement.
        if limit is not None:
            if not isinstance(limit, str) and not isinstance(limit, int):
                bulb_logger.error(
                    f'BULBSessionError("The \'limit\' parameter of the get() method of {cls.__name__} must be a string or an integer.")')
                raise BULBSessionError(
                    f"The 'limit' parameter of the get() method of {cls.__name__} must be a string or an integer.")

            else:
                limit_statement = f"LIMIT {limit}"

        # Build skip_statement and add its required variable.
        if skip is not None:
            if not isinstance(skip, str) and not isinstance(skip, int):
                bulb_logger.error(
                    f'BULBSessionError("The \'skip\' parameter of the get() method of {cls.__name__} must be a string or an integer.")')
                raise BULBSessionError(
                    f"The 'skip' parameter of the get() method of {cls.__name__} must be a string or an integer.")

            else:
                skip_statement = f"SKIP {skip}"

        # Build desc_statement.
        if not isinstance(desc, bool):
            bulb_logger.error(
                f'BULBSessionError("The \'desc\' parameter of the get() method of {cls.__name__} must be a boolean.")')
            raise BULBSessionError(
                f"The 'desc' parameter of the get() method of {cls.__name__} must be a boolean.")

        else:
            if desc is True:
                desc_statement = "DESC"

        request_statement = """
             %s
             %s
             %s
             %s
             %s
             %s
             %s
             %s
             """ % (match_statement,
                    where_statement,
                    with_statement,
                    order_by_statement,
                    desc_statement,
                    skip_statement,
                    limit_statement,
                    return_statement)

        if return_query is False:
            response = gdbh.r_transaction(request_statement)

            if response:
                if only is None:
                    fake_instances_list = []

                    for session_object in response:
                        fake_instances_list.append(cls.build_fake_instance(session_object["s"],
                                                                           forced_fake_instance_class=cls))

                    if uuid is not None or session_key is not None:
                        return fake_instances_list[0]

                    else:
                        return fake_instances_list

                else:
                    return response

            else:
                return None

        else:
            return request_statement

    @classmethod
    def count(cls, uuid=None, order_by=None, limit=None, skip=None, desc=False, only=None, filter=None, **extrafields):
        request_statement = cls.get(uuid=uuid, order_by=order_by, limit=limit, skip=skip, desc=desc, only=only,
                                    filter=filter, return_query=True, **extrafields)
        request_count_statement = request_statement.split("RETURN")[0] + "RETURN COUNT(s)"
        response = gdbh.r_transaction(request_count_statement)

        return response[0]["COUNT(s)"]

    @classmethod
    def exists(cls, session_key):
        response = cls.get(session_key=session_key)

        if response:
            return True

        else:
            return False

    @classmethod
    def delete_session(cls, session_key):
        response = cls.get(session_key=session_key)

        if response:
            gdbh.w_transaction("MATCH (s:Session {session_key:'%s'}) DETACH DELETE (s)" % session_key)

        else:
            bulb_logger.error(
                f'BULBSessionDoesNotExist("No session with session_key = \'{session_key}\'. So it cannot be deleted.")')
            raise BULBSessionDoesNotExist(f"No session with session_key = '{session_key}'. So it cannot be deleted.")

    @classmethod
    def clear_expired_sessions(cls):
        gdbh.r_transaction("""
            MATCH (s:Session)
            WHERE s.expire_date < datetime('%s')
            DETACH DELETE (s)
            """ % str(timezone.now()).replace(' ', 'T'))


def get_session_node_model():
    if settings.BULB_SESSION_NODE_MODEL_FILE == "bulb.contrib.sessions.node_models":
        return Session

    else:
        overloaded_session = None
        overloaded_session_module = importlib.import_module(settings.BULB_SESSION_NODE_MODEL_FILE)

        try:
            overloaded_session = overloaded_session_module.Session

        except AttributeError:
            bulb_logger.warning(
                f'BULBSessionWarning("You have defined BULB_SESSION_NODE_MODEL_FILE = \'{settings.BULB_SESSION_NODE_MODEL_FILE}\' but no Session node model was found in it. So the native Session node model will be used.")')
            warnings.warn(
                f"You have defined BULB_SESSION_NODE_MODEL_FILE = '{settings.BULB_SESSION_NODE_MODEL_FILE}' but no Session node model was found in it. So the native Session node model will be used.",
                BULBSessionWarning)

        else:
            return overloaded_session
        return Session
