from bulb.contrib.auth.hashers import _hash_password
from bulb.contrib.auth.exceptions import *
from bulb.db.exceptions import BULBNodeError
from bulb.utils.log import bulb_logger
from bulb.db.utils import make_uuid
from bulb.db import node_models
from bulb.db.base import gdbh
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
import importlib.util
import warnings
import datetime


BASE_DIR = settings.BASE_DIR


class FakeClass:
    pass


class GroupPermissionsRelationship(node_models.Relationship):
    rel_type = "CAN"
    direction = "from"
    start = "self"
    target = "Permission"
    auto = False
    on_delete = "PROTECT"
    unique = False


class UserPermissionsRelationship(node_models.Relationship):
    rel_type = "CAN"
    direction = "from"
    start = "self"
    target = "Permission"
    auto = False
    on_delete = "PROTECT"
    unique = False

    def get(self, direction="bi", returned="node", order_by=None, limit=None, skip=None, desc=False, distinct=False, only=None,
            only_user_perms=False):
        user_instance = self._self_node_instance
        if user_instance.is_active_user:
            permissions_list = []

            # Get user's permissions.
            user_permissions = super().get(direction="from", returned="node", order_by=order_by, limit=limit, skip=skip,
                                           desc=desc, distinct=distinct, only=only)

            if user_permissions is not None:
                for permission in user_permissions:
                    permissions_list.append(permission)

            if only_user_perms is False:
                # Get user's groups' permissions.
                groups = user_instance.groups.get(returned="node", direction="from")
                if groups is not None:
                    for group in groups:
                        group_permissions = group.permissions.get(direction="from", returned="node", order_by=order_by,
                                                                  limit=limit, skip=skip, desc=desc, distinct=distinct,
                                                                  only=only)

                        if group_permissions is not None:
                            for perm in group_permissions:
                                if perm not in permissions_list:
                                    permissions_list.append(perm)

            if permissions_list:
                return permissions_list

        return None


class UserGroupsRelationship(node_models.Relationship):
    rel_type = "IS_IN"
    direction = "from"
    start = "self"
    target = "Group"
    auto = False
    on_delete = "PROTECT"
    unique = False


class GroupUsersRelationship(node_models.Relationship):
    rel_type = "IS_IN"
    direction = "to"
    start = "User"
    target = "self"
    auto = False
    on_delete = "PROTECT"
    unique = False


class UserSessionRelationsip(node_models.Relationship):
    rel_type = "IS_SESSION_OF"
    direction = "to"
    start = "Session"
    target = "self"
    auto = False
    on_delete = "CASCADE"
    unique = True


class Permission(node_models.Node):

    codename = node_models.Property(unique=True,
                                    required=True)

    description = node_models.Property(unique=True,
                                       required=True)

    def __str__(self):
        return f'<Permission object(codename="{self.codename}", description="{self.description}")>'

    def __repr__(self):
        return f'<Permission object(codename="{self.codename}", description="{self.description}")>'

    def __hash__(self):
        return hash(self.codename) + hash(self.description)

    @classmethod
    def get(cls, uuid=None, codename=None, order_by=None, limit=None, skip=None, desc=False, only=None, filter=None, distinct=False,
            handmade=None, return_query=False):
        """
        This method allow the retrieving of Permission (or of one of its children classes) instances.

        :param codename (required if there is no uuid) : The codename of a permission to get an unique permission instance.

        :param uuid (required if there is no codename) : The Universal Unique Identifier of a node to get an unique instance.

        :param order_by (optional, default=None) : Must be the name of the property with which the returned datas will be sorted.
                                                   Examples : "datetime", "first_name", etc...

        :param limit (optional, default=None) : Must be an integer. This parameter defines the number of returned elements.

        :param skip (optional, default=None) : Must be an integer. This parameter defines the number of skipped elements. For example
                                               if self.skip = 3, the 3 first returned elements will be skipped.

        :param desc (optional, default=False) : Must be a boolean. If it is False the elements will be returned in an increasing order,
                                                but it is True, they will be returned in a descending order.

        :param only (optional, default=None) : Must be a list of field_names. If this parameter is filled, the return will not be Node
                                               instances, but a dict with "only" the mentioned fields.

        :param filter (optional, default=None) : Must be Q statement. You must use the Q class stored in bulb.db
                                                 Example: Q(name__contains="al") | Q(age__year__lte=8)

        :param distinct (optional, default=False) : Must be a boolean. If it is True, the returned list will be only composed with
                                                    unique elements.

        :param handmade: If this param is filled, no other must be filled. With 'handmade', you can insert your own get query and
                         the function will transform the objects returned by the database into Python instance of this class. WARNING :
                         Please consider using the gdbh.r_transaction() method (imported from bulb.db) if your request no returns full
                         Neo4j objects but a list of properties.
                         Examples :
                         ❌ : MATCH (p) RETURN p.first_name, p.last_name
                         ✅ : MATCH (p) RETURN p

                         In addition, note that the RETURN must absolutely be named 'p' like "permission".

        :param return_query (optional, default=False) : Must be a boolean. If true, the method will return the cypher query.

        :return: If uuid is None, a list will be returned. Else it will be a unique instance.
        """

        if handmade is None:

            where_statement = ""
            property_statement = ""
            order_by_statement = ""
            limit_statement = ""
            skip_statement = ""
            desc_statement = ""

            # Build the property_statement.
            if uuid is not None and codename is not None:
                property_statement = "{uuid:'%s', codename:'%s'}" % (uuid, codename)

            elif uuid is not None:
                property_statement = "{uuid:'%s'}" % uuid

            elif codename is not None:
                property_statement = "{codename:'%s'}" % codename

            # Build the match_statement.
            cyher_labels = node_models.DatabaseNode.format_labels_to_cypher(cls._get_labels())
            match_statement = f"MATCH (p:{cyher_labels} {property_statement})"

            # Build the where statement.
            if filter is not None:
                if not filter[0] != "n":
                    where_statement = "WHERE " + filter

                else:
                    where_statement = filter

                where_statement = where_statement.replace("n.", "p.")

            # Build the with_statement.
            with_statement = "WITH p"

            # Build order_by statements.
            if order_by is not None:
                order_by_statement = f"ORDER BY p.{order_by}"

            # Build return_statement statements.
            if not only:
                if not distinct:
                    return_statement = "RETURN (p)"

                else:
                    return_statement = "RETURN DISTINCT (p)"

            else:
                only_statement_list = []

                for element in only:
                    only_statement_list.append(f"p.{element}")

                only_statement = ", ".join(only_statement_list)

                if not distinct:
                    return_statement = f"RETURN {only_statement}"

                else:
                    return_statement = f"RETURN DISTINCT {only_statement}"

            # Build limit_statement.
            if limit is not None:
                if not isinstance(limit, str) and not isinstance(limit, int):
                    bulb_logger.error(
                        f'BULBNodeError("The \'limit\' parameter of the get() method of {cls.__name__} must be a string or an integer.")')
                    raise BULBNodeError(
                        f"The 'limit' parameter of the get() method of {cls.__name__} must be a string or an integer.")

                else:
                    limit_statement = f"LIMIT {limit}"

            # Build skip_statement and add its required variable.
            if skip is not None:
                if not isinstance(skip, str) and not isinstance(skip, int):
                    bulb_logger.error(
                        f'BULBNodeError("The \'skip\' parameter of the get() method of {cls.__name__} must be a string or an integer.")')
                    raise BULBNodeError(
                        f"The 'skip' parameter of the get() method of {cls.__name__} must be a string or an integer.")

                else:
                    skip_statement = f"SKIP {skip}"

            # Build desc_statement.
            if not isinstance(desc, bool):
                bulb_logger.error(
                    f'BULBNodeError("The \'desc\' parameter of the get() method of {cls.__name__} must be a boolean.")')
                raise BULBNodeError(
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

                        for permission_object in response:
                            fake_instances_list.append(cls.build_fake_instance(permission_object["p"],
                                                                               forced_fake_instance_class=cls))

                        if uuid is not None or codename is not None:
                            return fake_instances_list[0]
                        else:
                            return fake_instances_list

                    else:
                        return response

                else:
                    return None

            else:
                return request_statement

        else:
            response = gdbh.r_transaction(handmade)

            fake_instances_list = []

            for node_object in response:
                fake_instances_list.append(cls.build_fake_instance(node_object["p"],
                                                                   forced_fake_instance_class=cls))

            return fake_instances_list

    @classmethod
    def count(cls, uuid=None, codename=None, order_by=None, limit=None, skip=None, desc=False, only=None, filter=None, distinct=False,
              handmade=None, **extrafields):
        request_statement = cls.get(uuid=uuid, codename=codename, order_by=order_by, limit=limit, skip=skip, desc=desc, only=only,
                                    filter=filter, handmade=handmade, return_query=True, **extrafields)

        request_count_statement = None

        if not distinct:
            request_count_statement = request_statement.split("RETURN")[0] + "RETURN COUNT(p)"

        else:
            request_count_statement = request_statement.split("RETURN")[0] + "RETURN COUNT(DISTINCT p)"

        response = gdbh.r_transaction(request_count_statement)

        if not distinct:
            return response[0]["COUNT(p)"]

        else:
            return response[0]["COUNT(DISTINCT p)"]


def get_permission_node_model():
    if settings.BULB_PERMISSION_NODE_MODEL_FILE == "bulb.contrib.auth.node_models":
        return Permission

    else:
        overloaded_permission = None
        overloaded_permission_module = importlib.import_module(settings.BULB_PERMISSION_NODE_MODEL_FILE)

        try:
            overloaded_permission = overloaded_permission_module.Permission

        except AttributeError:
            bulb_logger.warning(
                f'BULBAuthNodeModelsWarning("You have defined BULB_PERMISSION_NODE_MODEL_FILE = \'{settings.BULB_PERMISSION_NODE_MODEL_FILE}\' but no Permission node model was found in it. So the native Permission node model will be used.")')
            warnings.warn(
                f"You have defined BULB_PERMISSION_NODE_MODEL_FILE = '{settings.BULB_PERMISSION_NODE_MODEL_FILE}' but no Permission node model was found in it. So the native Permission node model will be used.",
                BULBAuthNodeModelsWarning)

        else:
            return overloaded_permission
        return Permission


class Group(node_models.Node):

    name = node_models.Property(unique=True,
                                required=True)

    permissions = GroupPermissionsRelationship()

    users = GroupUsersRelationship()

    def __str__(self):
        return f'<Group object(name="{self.name}", uuid="{self.uuid}")>'

    def __repr__(self):
        return f'<Group object(name="{self.name}", uuid="{self.uuid}")>'

    @classmethod
    def get(cls, uuid=None, name=None, order_by=None, limit=None, skip=None, desc=False, only=None, filter=None, distinct=False,
            handmade=None, return_query=False):
        """
        This method allow the retrieving of Group (or of one of its children classes) instances.

        :param name (required if there is no uuid) : The name of a group to get an unique group instance.

        :param uuid (required if there is no name) : The Universal Unique Identifier of a node to get an unique instance.

        :param order_by (optional, default=None) : Must be the name of the property with which the returned datas will be sorted.
                                                   Examples : "datetime", "first_name", etc...

        :param limit (optional, default=None) : Must be an integer. This parameter defines the number of returned elements.

        :param skip (optional, default=None) : Must be an integer. This parameter defines the number of skipped elements. For example
                                               if self.skip = 3, the 3 first returned elements will be skipped.

        :param desc (optional, default=False) : Must be a boolean. If it is False the elements will be returned in an increasing order,
                                                but it is True, they will be returned in a descending order.

        :param only (optional, default=None) : Must be a list of field_names. If this parameter is filled, the return will not be Node
                                               instances, but a dict with "only" the mentioned fields.

        :param filter (optional, default=None) : Must be Q statement. You must use the Q class stored in bulb.db
                                                 Example: Q(name__contains="al") | Q(age__year__lte=8)

        :param distinct (optional, default=False) : Must be a boolean. If it is True, the returned list will be only composed with
                                                    unique elements.

        :param handmade: If this param is filled, no other must be filled. With 'handmade', you can insert your own get query and
                         the function will transform the objects returned by the database into Python instance of this class. WARNING :
                         Please consider using the gdbh.r_transaction() method (imported from bulb.db) if your request no returns full
                         Neo4j objects but a list of properties.
                         Examples :
                         ❌ : MATCH (g) RETURN g.first_name, g.last_name
                         ✅ : MATCH (g) RETURN g

                         In addition, note that the RETURN must absolutely be named 'g' like "group".

        :param return_query (optional, default=False) : Must be a boolean. If true, the method will return the cypher query.

        :return: If uuid is None, a list will be returned. Else it will be a unique instance.
        """

        if handmade is None:

            where_statement = ""
            property_statement = ""
            order_by_statement = ""
            limit_statement = ""
            skip_statement = ""
            desc_statement = ""

            # Build the property_statement.
            if uuid is not None and name is not None:
                property_statement = "{uuid:'%s', name:'%s'}" % (uuid, name)

            elif uuid is not None:
                property_statement = "{uuid:'%s'}" % uuid

            elif name is not None:
                property_statement = "{name:'%s'}" % name

            # Build the match_statement.
            cyher_labels = node_models.DatabaseNode.format_labels_to_cypher(cls._get_labels())
            match_statement = f"MATCH (g:{cyher_labels} {property_statement})"

            # Build the where statement.
            if filter is not None:
                if not filter[0] != "n":
                    where_statement = "WHERE " + filter

                else:
                    where_statement = filter

                where_statement = where_statement.replace("n.", "g.")

            # Build the with_statement.
            with_statement = "WITH g"

            # Build order_by statements.
            if order_by is not None:
                order_by_statement = f"ORDER BY g.{order_by}"

            # Build return_statement statements.
            if not only:
                if not distinct:
                    return_statement = "RETURN (g)"

                else:
                    return_statement = "RETURN DISTINCT (g)"

            else:
                only_statement_list = []

                for element in only:
                    only_statement_list.append(f"g.{element}")

                only_statement = ", ".join(only_statement_list)

                if not distinct:
                    return_statement = f"RETURN {only_statement}"

                else:
                    return_statement = f"RETURN DISTINCT {only_statement}"

            # Build limit_statement.
            if limit is not None:
                if not isinstance(limit, str) and not isinstance(limit, int):
                    bulb_logger.error(
                        f'BULBNodeError("The \'limit\' parameter of the get() method of {cls.__name__} must be a string or an integer.")')
                    raise BULBNodeError(
                        f"The 'limit' parameter of the get() method of {cls.__name__} must be a string or an integer.")

                else:
                    limit_statement = f"LIMIT {limit}"

            # Build skip_statement and add its required variable.
            if skip is not None:
                if not isinstance(skip, str) and not isinstance(skip, int):
                    bulb_logger.error(
                        f'BULBNodeError("The \'skip\' parameter of the get() method of {cls.__name__} must be a string or an integer.")')
                    raise BULBNodeError(
                        f"The 'skip' parameter of the get() method of {cls.__name__} must be a string or an integer.")

                else:
                    skip_statement = f"SKIP {skip}"

            # Build desc_statement.
            if not isinstance(desc, bool):
                bulb_logger.error(
                    f'BULBNodeError("The \'desc\' parameter of the get() method of {cls.__name__} must be a boolean.")')
                raise BULBNodeError(
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

                        for group_object in response:
                            fake_instances_list.append(cls.build_fake_instance(group_object["g"],
                                                                               forced_fake_instance_class=cls))

                        if uuid is not None or name is not None:
                            return fake_instances_list[0]
                        else:
                            return fake_instances_list

                    else:
                        return response

                else:
                    return None

            else:
                return request_statement

        else:
            response = gdbh.r_transaction(handmade)

            fake_instances_list = []

            for node_object in response:
                fake_instances_list.append(cls.build_fake_instance(node_object["g"],
                                                                   forced_fake_instance_class=cls))

            return fake_instances_list

    @classmethod
    def count(cls, uuid=None, name=None, order_by=None, limit=None, skip=None, desc=False, only=None, filter=None, distinct=False,
              handmade=None, **extrafields):
        request_statement = cls.get(uuid=uuid, name=name, order_by=order_by, limit=limit, skip=skip, desc=desc, only=only,
                                    filter=filter, handmade=handmade, return_query=True, **extrafields)
        request_count_statement = None

        if not distinct:
            request_count_statement = request_statement.split("RETURN")[0] + "RETURN COUNT(g)"

        else:
            request_count_statement = request_statement.split("RETURN")[0] + "RETURN COUNT(DISTINCT g)"

        response = gdbh.r_transaction(request_count_statement)

        if not distinct:
            return response[0]["COUNT(g)"]

        else:
            return response[0]["COUNT(DISTINCT g)"]


def get_group_node_model():
    if settings.BULB_GROUP_NODE_MODEL_FILE == "bulb.contrib.auth.node_models":
        return Group

    else:
        overloaded_group = None
        overloaded_group_module = importlib.import_module(settings.BULB_GROUP_NODE_MODEL_FILE)

        try:
            overloaded_group = overloaded_group_module.Group

        except AttributeError:
            bulb_logger.warning(
                f'BULBAuthNodeModelsWarning("You have defined BULB_GROUP_NODE_MODEL_FILE = \'{settings.BULB_GROUP_NODE_MODEL_FILE}\' but no Group node model was found in it. So the native Group node model will be used.")')
            warnings.warn(
                f"You have defined BULB_GROUP_NODE_MODEL_FILE = '{settings.BULB_GROUP_NODE_MODEL_FILE}' but no Group node model was found in it. So the native Group node model will be used.",
                BULBAuthNodeModelsWarning)

        else:
            return overloaded_group
        return Group


class EmptyRelationship(node_models.Relationship):
    rel_type = ""


class AnonymousUser:
    is_super_user = False
    is_staff_user = False
    is_active_user = False
    uuid = None
    first_name = None
    last_name = None
    email = None
    password = None
    registration_datetime = None
    session = EmptyRelationship()
    groups = EmptyRelationship()
    permissions = EmptyRelationship()

    def __str__(self):
        return 'AnonymousUser'

    def __repr__(self):
        return 'AnonymousUser'

    @classmethod
    def create(cls, **extrafields):
        bulb_logger.error(f'NotImplementedError("bulb doesn\'t provide a DB representation for AnonymousUser.")')
        raise NotImplementedError("bulb doesn't provide a DB representation for AnonymousUser.")

    @classmethod
    def create_super_user(cls, **extrafields):
        bulb_logger.error(f'NotImplementedError("bulb doesn\'t provide a DB representation for AnonymousUser.")')
        raise NotImplementedError("bulb doesn't provide a DB representation for AnonymousUser.")

    @classmethod
    def get(cls, uuid_or_email):
        return cls()

    def update(self, user_property, new_user_property_value):
        bulb_logger.error(f'NotImplementedError("bulb doesn\'t provide a DB representation for AnonymousUser.")')
        raise NotImplementedError("bulb doesn't provide a DB representation for AnonymousUser.")

    def delete(self):
        bulb_logger.error(f'NotImplementedError("bulb doesn\'t provide a DB representation for AnonymousUser.")')
        raise NotImplementedError("bulb doesn't provide a DB representation for AnonymousUser.")

    def set_password(self, new_password):
        bulb_logger.error(f'NotImplementedError("bulb doesn\'t provide a DB representation for AnonymousUser.")')
        raise NotImplementedError("bulb doesn't provide a DB representation for AnonymousUser.")

    def has_perm(self, permission_code_name):
        return False


def get_anonymoususer_node_model():
    if settings.BULB_ANONYMOUSUSER_NODE_MODEL_FILE == "bulb.contrib.auth.node_models":
        return AnonymousUser
    else:
        overloaded_anonymoususer = None
        overloaded_anonymoususer_module = importlib.import_module(settings.BULB_ANONYMOUSUSER_NODE_MODEL_FILE)
        try:
            overloaded_anonymoususer = overloaded_anonymoususer_module.AnonymousUser
        except AttributeError:
            bulb_logger.warning(
                f'BULBAuthNodeModelsWarning("You have defined BULB_ANONYMOUSUSER_NODE_MODEL_FILE = \'{settings.BULB_ANONYMOUSUSER_NODE_MODEL_FILE}\' but no AnonymousUser node model was found in it. So the native AnonymousUser node model will be used.")')
            warnings.warn(
                f"You have defined BULB_ANONYMOUSUSER_NODE_MODEL_FILE = '{settings.BULB_ANONYMOUSUSER_NODE_MODEL_FILE}' but no AnonymousUser node model was found in it. So the native AnonymousUser node model will be used.",
                BULBAuthNodeModelsWarning)
        else:
            return overloaded_anonymoususer
        return AnonymousUser


class User(node_models.Node):

    # Default groups
    is_super_user = node_models.Property(default=False)

    is_staff_user = node_models.Property(default=False)

    is_active_user = node_models.Property(default=True)

    first_name = node_models.Property(required=True)

    last_name = node_models.Property(required=True)

    email = node_models.Property(required=True,
                                 unique=True)

    password = node_models.Property(required=True)

    registration_datetime = node_models.Property(default=datetime.datetime.now)

    permissions = UserPermissionsRelationship()

    groups = UserGroupsRelationship()

    session = UserSessionRelationsip()

    email_confirmation_key = None

    email_is_confirmed = None

    if settings.BULB_REGISTRATION_USE_EMAIL_CONFIRMATION:
        email_confirmation_key = node_models.Property()

        email_is_confirmed = node_models.Property(default=False)

    def __str__(self):
        return f'<User object(first_name="{self.first_name}", last_name="{self.last_name}", uuid="{self.uuid}")>'

    def __repr__(self):
        return f'<User object(first_name="{self.first_name}", last_name="{self.last_name}", uuid="{self.uuid}")>'

    @classmethod
    def create(cls, **extrafields):

        extrafields.setdefault('is_super_user', False)
        extrafields.setdefault('is_staff_user', False)
        extrafields.setdefault('is_active_user', True)

        extrafields['password'] = _hash_password(extrafields['password'])

        new_user = cls(**extrafields)

        if settings.BULB_REGISTRATION_USE_EMAIL_CONFIRMATION:
            # Generate the email confirmation key.
            email_confirmation_key = make_uuid()

            # Apply it to the new User instance.
            new_user.update('email_confirmation_key', email_confirmation_key)

            target_email = extrafields[settings.BULB_USER_EMAIL_PROPERTY_NAME]
            confirmation_url = settings.BULB_CONFIRMATION_VIEW_PATH + email_confirmation_key

            send_mail(
                from_email=settings.BULB_EMAIL_CONFIRMATION_SENDER_NAME,
                subject=settings.BULB_EMAIL_CONFIRMATION_SUBJECT,
                recipient_list=[f"{target_email}"],
                message=settings.BULB_EMAIL_CONFIRMATION_DEFAULT_MESSAGE + confirmation_url,
                html_message=render_to_string(settings.BULB_EMAIL_CONFIRMATION_TEMPLATE_PATH,
                                              {"confirmation_url": confirmation_url}))

        return new_user

    @classmethod
    def create_super_user(cls, **extrafields):
        extrafields.setdefault('is_super_user', True)
        extrafields.setdefault('is_staff_user', True)
        extrafields.setdefault('is_active_user', True)

        extrafields['password'] = _hash_password(extrafields['password'])

        is_super_user = extrafields.get('is_super_user')
        is_staff_user = extrafields.get('is_staff_user')
        if not is_super_user:
            bulb_logger.error('ValueError(\'A SuperUser must have "is_super_user = True".\')')
            raise ValueError('A SuperUser must have "is_super_user = True".')

        elif not is_staff_user:
            bulb_logger.error('ValueError(\'A SuperUser must have "is_staff_user = True".\')')
            raise ValueError('A SuperUser must have "is_staff_user = True".')

        else:
            new_super_user = User(**extrafields)

            return new_super_user

    @classmethod
    def get(cls, uuid=None, email=None, email_confirmation_key=None, order_by=None, limit=None, skip=None, desc=False, only=None,
            filter=None, distinct=False, handmade=None, return_query=False):
        """
        This method allow the retrieving of User (or of one of its children classes) instances.

        :param email (required if there is neither uuid nor email_confirmation_key) : The email of a user to get an unique user instance.

        :param uuid (required if there is neither email nor email_confirmation_key) : The Universal Unique Identifier of a node to get
                                                                                      an unique instance.

        :param email_confirmation_key (required if there is neither email nor uuid) : The confirmation key for the email validation part.

        :param order_by (optional, default=None) : Must be the name of the property with which the returned datas will be sorted.
                                                   Examples : "datetime", "first_name", etc...

        :param limit (optional, default=None) : Must be an integer. This parameter defines the number of returned elements.

        :param skip (optional, default=None) : Must be an integer. This parameter defines the number of skipped elements. For example
                                               if self.skip = 3, the 3 first returned elements will be skipped.

        :param desc (optional, default=False) : Must be a boolean. If it is False the elements will be returned in an increasing order,
                                                but it is True, they will be returned in a descending order.

        :param only (optional, default=None) : Must be a list of field_names. If this parameter is filled, the return will not be Node
                                               instances, but a dict with "only" the mentioned fields.

        :param filter (optional, default=None) : Must be Q statement. You must use the Q class stored in bulb.db
                                                 Example: Q(name__contains="al") | Q(age__year__lte=8)

        :param distinct (optional, default=False) : Must be a boolean. If it is True, the returned list will be only composed with
                                                    unique elements.

        :param handmade: If this param is filled, no other must be filled. With 'handmade', you can insert your own get query and
                         the function will transform the objects returned by the database into Python instance of this class. WARNING :
                         Please consider using the gdbh.r_transaction() method (imported from bulb.db) if your request no returns full
                         Neo4j objects but a list of properties.
                         Examples :
                         ❌ : MATCH (u) RETURN u.first_name, u.last_name
                         ✅ : MATCH (u) RETURN u

                         In addition, note that the RETURN must absolutely be named 'u' like "user".

        :param return_query (optional, default=False) : Must be a boolean. If true, the method will return the cypher query.

        :return: If uuid is None, a list will be returned. Else it will be a unique instance.
        """

        if handmade is None:
            where_statement = ""
            property_statement = ""
            order_by_statement = ""
            limit_statement = ""
            skip_statement = ""
            desc_statement = ""

            # Build the property_statement.
            if uuid is not None and email is not None:
                property_statement = "{uuid:'%s', email:'%s'}" % (uuid, email)

            elif uuid is not None:
                property_statement = "{uuid:'%s'}" % uuid

            elif email is not None:
                property_statement = "{email:'%s'}" % email

            elif email_confirmation_key is not None:
                property_statement = "{email_confirmation_key:'%s'}" % email_confirmation_key

            # Build the match_statement.
            cyher_labels = node_models.DatabaseNode.format_labels_to_cypher(cls._get_labels())
            match_statement = f"MATCH (u:{cyher_labels} {property_statement})"

            # Build the where statement.
            if filter is not None:
                # where_statement = "WHERE " + filter #removed to fix

                if not filter[0] != "n":
                    where_statement = "WHERE " + filter

                else:
                    where_statement = filter

                where_statement = where_statement.replace("n.", "u.")

            # Build the with_statement.
            with_statement = "WITH u"

            # Build order_by statements.
            if order_by is not None:
                order_by_statement = f"ORDER BY u.{order_by}"

            # Build return_statement statements.
            if not only:
                if not distinct:
                    return_statement = "RETURN (u)"

                else:
                    return_statement = "RETURN DISTINCT (u)"

            else:
                only_statement_list = []

                for element in only:
                    only_statement_list.append(f"u.{element}")

                only_statement = ", ".join(only_statement_list)

                if not distinct:
                    return_statement = f"RETURN {only_statement}"

                else:
                    return_statement = f"RETURN DISTINCT {only_statement}"

            # Build limit_statement.
            if limit is not None:
                if not isinstance(limit, str) and not isinstance(limit, int):
                    bulb_logger.error(
                        f'BULBNodeError("The \'limit\' parameter of the get() method of {cls.__name__} must be a string or an integer.")')
                    raise BULBNodeError(
                        f"The 'limit' parameter of the get() method of {cls.__name__} must be a string or an integer.")

                else:
                    limit_statement = f"LIMIT {limit}"

            # Build skip_statement and add its required variable.
            if skip is not None:
                if not isinstance(skip, str) and not isinstance(skip, int):
                    bulb_logger.error(
                        f'BULBNodeError("The \'skip\' parameter of the get() method of {cls.__name__} must be a string or an integer.")')
                    raise BULBNodeError(
                        f"The 'skip' parameter of the get() method of {cls.__name__} must be a string or an integer.")

                else:
                    skip_statement = f"SKIP {skip}"

            # Build desc_statement.
            if not isinstance(desc, bool):
                bulb_logger.error(
                    f'BULBNodeError("The \'desc\' parameter of the get() method of {cls.__name__} must be a boolean.")')
                raise BULBNodeError(
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

                        for user_object in response:
                            fake_instances_list.append(cls.build_fake_instance(user_object["u"],
                                                                               forced_fake_instance_class=cls))

                        if uuid is not None or email is not None or email_confirmation_key is not None:
                            return fake_instances_list[0]

                        else:
                            return fake_instances_list

                    else:
                        return response

                else:
                    if uuid is not None or email is not None or email_confirmation_key is not None:
                        if settings.BULB_ANONYMOUSUSER_NODE_MODEL_FILE: # TODO : This line is maybe useless, check it.
                            AnonymousUser_node_model = get_anonymoususer_node_model()
                            return AnonymousUser_node_model()

                    else:
                        return None
            else:
                return request_statement

        else:
            response = gdbh.r_transaction(handmade)

            fake_instances_list = []

            for node_object in response:
                fake_instances_list.append(cls.build_fake_instance(node_object["u"],
                                                                   forced_fake_instance_class=cls))

            return fake_instances_list


    @classmethod
    def count(cls, uuid=None, email=None,  email_confirmation_key=None, order_by=None, limit=None, skip=None, desc=False, only=None,
              filter=None, distinct=False, handmade=None, **extrafields):
        request_statement = cls.get(uuid=uuid, email=email,  email_confirmation_key=email_confirmation_key, order_by=order_by,
                                    limit=limit, skip=skip, desc=desc, only=only, filter=filter, handmade=handmade, return_query=True,
                                     **extrafields)

        request_count_statement = None

        if not distinct:
            request_count_statement = request_statement.split("RETURN")[0] + "RETURN COUNT(u)"

        else:
            request_count_statement = request_statement.split("RETURN")[0] + "RETURN COUNT(DISTINCT u)"

        response = gdbh.r_transaction(request_count_statement)

        if not distinct:
            return response[0]["COUNT(u)"]

        else:
            return response[0]["COUNT(DISTINCT u)"]

    def set_password(self, new_password):
        self.update("password", _hash_password(new_password))

    def has_perm(self, permission_code_name):
        if self.is_super_user:
            return True

        if not self.is_active_user:
            return False

        else:
            permission_to_test = Permission.get(codename=permission_code_name)
            all_user_permissions = self.permissions.get()

            if all_user_permissions is not None:
                if permission_to_test in all_user_permissions:
                    return True
            return False


def get_user_node_model():
    if settings.BULB_USER_NODE_MODEL_FILE == "bulb.contrib.auth.node_models":
        return User

    else:
        overloaded_user = None
        overloaded_user_module = importlib.import_module(settings.BULB_USER_NODE_MODEL_FILE)

        try:
            overloaded_user = overloaded_user_module.User

        except AttributeError:
            bulb_logger.warning(
                f'BULBAuthNodeModelsWarning("You have defined BULB_USER_NODE_MODEL_FILE = \'{settings.BULB_USER_NODE_MODEL_FILE}\' but no User node model was found in it. So the native User node model will be used.")')
            warnings.warn(
                f"You have defined BULB_USER_NODE_MODEL_FILE = '{settings.BULB_USER_NODE_MODEL_FILE}' but no User node model was found in it. So the native User node model will be used.",
                BULBAuthNodeModelsWarning)

        else:
            return overloaded_user
        return User
