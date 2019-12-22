from bulb.contrib.statictools.compressor import compress_file_and_build_paths
from bulb.db.utils import make_uuid, compare_different_modules_classes
from bulb.utils import get_all_node_models
from bulb.sftp_and_cdn.sftp import SFTP
from bulb.utils.log import bulb_logger
from bulb.db.exceptions import *
from bulb.db import gdbh, Q
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.conf import settings
import datetime
import warnings
import inspect
import neotime
import os

BASE_DIR = os.environ["BASE_DIR"]


class FakeClass:
    pass


class DatabaseNode:
    """
    This class has tools to :
    - Transform Python objects like lists and dictionaries in a Cypher format : format_labels_to_cypher(), format_properties_to_cypher().
    - Create a node in the database : create()

    :param current_object_labels_list (optional, default=None) : a list of all the node's labels. No labels = None. Default = None

    :param current_object_properties_dict (optional, default=None) : a dictionary of all the node's properties, where keys are the
                                                                     names of the properties and values their values.
                                                                     No properties = None. Default = None

    :param related_class_properties_fields_dict (optional, default=None): a dictionary of all the node's properties, where keys are
                                                                          the names of the properties and values their Property
                                                                          instance.
    """

    def __init__(self,
                 current_object_labels_list=None,
                 current_object_properties_dict=None,
                 related_class_properties_fields_dict=None):

        self.current_object_labels_list = current_object_labels_list
        self.current_object_properties_dict = current_object_properties_dict
        self.related_class_properties_fields_dict = related_class_properties_fields_dict

        self.returned_node_object = None

        self.create()

    def create(self):
        """
        This method handle datas' formatting to cypher language, and the node's creation in the database.
        :return: It return the created node.
        """
        object_labels = self.__class__.format_labels_to_cypher(self.current_object_labels_list)
        object_properties = self.__class__.format_properties_to_cypher(self.related_class_properties_fields_dict,
                                                                       self.current_object_properties_dict)

        response = gdbh.w_transaction('CREATE (n:%s %s) RETURN (n)' % (object_labels, object_properties))
        self.returned_node_object = response[0]["n"]

    @classmethod
    def format_labels_to_cypher(cls, object_labels_list):
        """
        This method converts labels list format in a cypher labels format.

        :return: Cypher formatted labels.
        """
        render = []

        if isinstance(object_labels_list, list):
            for label in object_labels_list:
                render.append(label)
            return ':'.join(render)

        else:
            bulb_logger.error('BULBNodeLabelsInitializationError("\'labels_list\' attribute must be a list.")')
            raise BULBNodeLabelsInitializationError("'labels_list' attribute must be a list.")

    @classmethod
    def format_properties_to_cypher(cls, class_properties_dict, object_properties_dict):
        """
        This method converts properties dict format in a cypher properties format.

        :return: Cypher formatted properties.
        """

        if isinstance(object_properties_dict, dict):
            render = []

            for field_name, field_value in class_properties_dict.items():
                for key, value in object_properties_dict.items():
                    if field_name == key:

                        # Integer, float, boolean and list handling.
                        if isinstance(value, int) or isinstance(value, float) or isinstance(value, bool) or isinstance(value, list):
                            render.append(f"{key}: {value}")

                        # Datetime handling.
                        elif isinstance(value, datetime.datetime):
                            render.append(f"{key}: datetime('{str(value).replace(' ', 'T')}')")

                        # Date handling.
                        elif isinstance(value, datetime.date):
                            render.append(f"{key}: date('{str(value)}')")

                        # Time handling.
                        elif isinstance(value, datetime.time):
                            render.append(f"{key}: time('{str(value)}')")

                        # String handling.
                        elif isinstance(value, str):
                            # Escape quotes to prevent cypher syntax errors.
                            rendered_value = value.replace('"', '\\"').replace("'", "\\'")
                            render.append(f"{key}: '{rendered_value}'")

                        # Other
                        else:
                            render.append(f"{key}: '{value}'")

            return '{' + ', '.join(render) + '}'

        else:
            bulb_logger.error('BULBNodeLabelsInitializationError("\'object_properties_dict\' attribute must be a dict.")')
            raise BULBNodeLabelsInitializationError("'object_properties_dict' attribute must be a dict.")


class Property:
    """
    This class can be directly instantiate, but could be also overridden to create specific properties model.

    :param (optional, default=None) content: The content is the value of a property.

    :param (optional, default=False) required: If set on True, and if the content of the property is empty, an error will be raised.

    :param (optional, default=False) unique: If set on True, and if the content of the property combination key+content is already
                                             in the database, an error will be raised.

    :param (optional, default=None) default: A default value that will fill the content if is empty.

    :param (optional, default=False) sftp: If set on True, and if the value is a file object, it will be stored on the SFTP server.

    """

    def __init__(self, content=None, required=False, unique=False, default=None, sftp=False):
        self.content = content
        self.required = required
        self.unique = unique
        self.default = default
        self.sftp = sftp

    @staticmethod
    def _build(node_or_rel_object, recovered_fields_values_dict):
        """
        This method take a Node object and datas recovered during its instantiation and _build a dictionary that
        contains key/content combinations for each property of the object.

        :param node_or_rel_object: An instance of the Node class.

        :param recovered_fields_values_dict: The dictionary of values recovered during the instantiation of the
                                             node_model class.

        :return: A dictionary that contains key+content combinations for the given object.
                 NB : All property without content nor 'default' parameter, will be filled by 'None'.
        """
        current_object_properties_dict = {}

        # All the attributes (representing the properties of the Node) of the current node class.
        class_properties_dict = node_or_rel_object.properties_fields

        # List that contains keys-values tuple of the parameters of the instance (a = SomeClass(key=value, key...)
        not_defined_fields = [field_item for field_item in class_properties_dict.items()]

        for field_name, field_content in class_properties_dict.items():
            if field_content._check_property_datas(node_or_rel_object, field_name, recovered_fields_values_dict):

                for key, value in recovered_fields_values_dict.items():
                    if value is not None:

                        # Check properties initial fields and recovered properties datas during instanciation
                        if key == field_name:
                            not_defined_fields.remove((field_name, field_content))

                            # Handle sftp fields:
                            if eval(f"node_or_rel_object.__class__.{key}") is not None:

                                if eval(f"node_or_rel_object.__class__.{key}.sftp"):

                                    if not isinstance(value, InMemoryUploadedFile) and not isinstance(value, TemporaryUploadedFile):

                                        if value == "None" or value == "":
                                            setattr(node_or_rel_object, key, value)
                                            current_object_properties_dict[key] = value

                                        else:
                                            bulb_logger.error(
                                                f'BULBPropertyError("The property \'{key}\' is configured with \'sftp=True\' but its value is neither a file nor \'None\'.")')
                                            raise BULBPropertyError(
                                                f"The property '{key}' is configured with 'sftp=True' but its value is neither a file nor 'None'.")

                                    else:
                                        temporary_local_file_path, remote_file_path = compress_file_and_build_paths(value)

                                        with SFTP.connect() as sftp:
                                            try:
                                                sftp.put(temporary_local_file_path, remote_file_path)

                                            # Check and create default storage folders if they are not already created.
                                            except IOError:
                                                if not sftp.exists("/www/staticfiles"):
                                                    sftp.mkdir("/www/staticfiles")

                                                if not sftp.exists("/www/staticfiles/content"):
                                                    sftp.mkdir("/www/staticfiles/content")

                                                if not sftp.exists("/www/staticfiles/content/img"):
                                                    sftp.mkdir("/www/staticfiles/content/img")

                                                if not sftp.exists("/www/staticfiles/content/pdf"):
                                                    sftp.mkdir("/www/staticfiles/content/pdf")

                                                if not sftp.exists("/www/staticfiles/content/svg"):
                                                    sftp.mkdir("/www/staticfiles/content/svg")

                                                sftp.put(temporary_local_file_path, remote_file_path)

                                        os.remove(temporary_local_file_path)

                                        full_stored_file_path_list = (settings.BULB_SFTP_PULL_URL + remote_file_path).split("/")
                                        full_stored_file_path_list.pop(3)
                                        full_stored_file_path = "/".join(full_stored_file_path_list)

                                        setattr(node_or_rel_object, key, full_stored_file_path)
                                        current_object_properties_dict[key] = full_stored_file_path

                                # Callable value handling.
                                elif callable(value):
                                    value = value()
                                    setattr(node_or_rel_object, key, value)
                                    current_object_properties_dict[key] = value

                                # Other.
                                else:
                                    setattr(node_or_rel_object, key, value)
                                    current_object_properties_dict[key] = value

        # Treat the undefined fields
        for field_item in not_defined_fields:
            if field_item[1].default is not None:
                if callable(field_item[1].default):
                    callable_result = field_item[1].default()

                    setattr(node_or_rel_object, field_item[0], callable_result)
                    current_object_properties_dict[field_item[0]] = callable_result

                else:
                    setattr(node_or_rel_object, field_item[0], field_item[1].default)
                    current_object_properties_dict[field_item[0]] = field_item[1].default

            else:
                setattr(node_or_rel_object, field_item[0], None)
                current_object_properties_dict[field_item[0]] = None

        return current_object_properties_dict

    def _check_property_datas(self, node_or_rel_object, property_name, recovered_fields_values_dict):
        """
        This method checks and enforces the restrictions (required, unique, etc...) of a field.

        :param (required) node_or_rel_object: The related node_model's instance.

        :param (required) property_name: The name of the property field to check.

        :param (required) recovered_fields_values_dict: The dictionary of values recovered during the instantiation
                                                        of the node_model class.

        :return:
        """

        try:
            if isinstance(recovered_fields_values_dict[property_name], str):
                property_value = recovered_fields_values_dict[property_name].replace('"', '\\"').replace("'", "\\'")

            else:
                property_value = recovered_fields_values_dict[property_name]

        except KeyError:
            # Check if a property is 'required' :
            if self.required and self.default is None:

                # Support "all in node" Relationship syntax.
                if isinstance(node_or_rel_object, Relationship):
                    relationship_name = node_or_rel_object._name
                    relationship_related_node_name = node_or_rel_object._self_node_instance.__class__.__name__

                    bulb_logger.error(
                        f'BULBRequiredConstraintError("The \'{relationship_name}\' relationship of an instance of {relationship_related_node_name} must have a/an \'{property_name}\'.")')
                    raise BULBRequiredConstraintError(
                        f"The '{relationship_name}' relationship of an instance of {relationship_related_node_name} must have a/an '{property_name}'.")

                # Support Node and "distinct" Relationship syntaxes.
                else:
                    bulb_logger.error(
                        'BULBRequiredConstraintError("An instance of {node_or_rel_object.__class__.__name__} must have a/an \'{property_name}\'.")')
                    raise BULBRequiredConstraintError(
                        f"An instance of {node_or_rel_object.__class__.__name__} must have a/an '{property_name}'.")

        else:
            # Check if a property is 'unique' :
            if self.unique:

                if Node in node_or_rel_object.__class__.__mro__:
                    cypher_syntax_node_or_rel_object_labels = DatabaseNode.format_labels_to_cypher(node_or_rel_object.labels,)
                    # Try to get an instance of the current node class with the same property
                    if isinstance(property_value, str):
                        query = 'MATCH (n:%s) WHERE n.%s = "%s" RETURN (n)' % (cypher_syntax_node_or_rel_object_labels,
                                                                               property_name,
                                                                               property_value)
                        result = gdbh.r_transaction(query)

                    else:
                        query = 'MATCH (n:%s) WHERE n.%s = %s RETURN (n)' % (cypher_syntax_node_or_rel_object_labels,
                                                                             property_name,
                                                                             property_value)
                        result = gdbh.r_transaction(query)

                    # If an instance is found, raise an error
                    if result:
                        bulb_logger.error(
                            f'BULBUniqueConstraintError("An instance of {node_or_rel_object.__class__.__name__} must have an UNIQUE \'{property_name}\'.")')
                        raise BULBUniqueConstraintError(
                            f"An instance of {node_or_rel_object.__class__.__name__} must have an UNIQUE '{property_name}'.")

                    else:
                        return True

                elif Relationship in node_or_rel_object.__class__.__mro__:
                    # Try to get an instance of the current relationship class with the same property
                    if isinstance(property_value, str):
                        query = 'MATCH ()-[r:%s]->() WHERE r.%s = "%s" RETURN (r)' % (node_or_rel_object.rel_type,
                                                                                      property_name,
                                                                                      property_value)
                        result = gdbh.r_transaction(query)

                    else:
                        query = 'MATCH ()-[r:%s]->() WHERE r.%s = %s RETURN (r)' % (node_or_rel_object.rel_type,
                                                                                    property_name,
                                                                                    property_value)
                        result = gdbh.r_transaction(query)

                    # If an instance is found, raise an error
                    if result:
                        bulb_logger.error(
                            f'BULBUniqueConstraintError("An instance of {node_or_rel_object.__class__.__name__} must have an UNIQUE \'{property_name}\'.")')
                        raise BULBUniqueConstraintError(
                            f"An instance of {node_or_rel_object.__class__.__name__} must have an UNIQUE '{property_name}'.")

                    else:
                        return True
            else:
                return True

        finally:
            # Checks if a property is not be at the same time 'required' and with a 'default' value :
            if self.required and self.default is not None:
                bulb_logger.error(
                    'BULBPropertyError("A property must not have \'required=True\' and a \'default\' value.")')
                raise BULBPropertyError("A property must not have \'required=True\' and a \'default\' value.")


class BaseNodeAndRelationship:

    # The UUID is the common property that all nodes have.
    uuid = Property(default=make_uuid,
                    unique=True)

    def __str__(self):
        return f'<{self.__class__.__name__} object(uuid="{self.uuid}")>'

    def __repr__(self):
        return f'<{self.__class__.__name__} object(uuid="{self.uuid}")>'

    def __eq__(self, other):
        other_uuid = None
        try:
            other_uuid = other.uuid

        except AttributeError:
            return False

        else:
            if self.uuid == other_uuid:
                return True
            return False

    @classmethod
    def _get_property_fields(cls, additional_fields_dict=None):
        """
        This method detects and regroups in a dictionary, all property fields of a Node instance. Then, it returns the
        dictionary.

        :param additional_fields_dict (optional, default=None) : An additional dict where the scripts will go to search the property
                                                                 fields.

        :return: A dictionary of all Node instance's properties.
        """
        print("\n\n\nSTART OF TEST ZONE\n\n\n")

        properties_dict = {}

        # Retrieve the properties declared in the class and those declared in all these parents: allow class inheritance.
        class_dict = cls.__dict__.copy()

        # Collect keys of properties that have None as value to remove them of the properties_dict
        none_properties = []

        for mro_class in cls.__mro__:
            for key, value in mro_class.__dict__.items():
                if value is not None:
                    class_dict[key] = value

                else:
                    none_properties.append(key)

        # Support "all in node" Relationship syntax.
        if additional_fields_dict is not None:
            class_dict.update(additional_fields_dict)

        for k, v in class_dict.items():
            if isinstance(v, Property) or Property in v.__class__.__mro__:
                properties_dict[k] = v

        for key in none_properties:
            try:
                del properties_dict[key]
            except:
                pass

        return properties_dict

    @classmethod
    def build_fake_instance(cls, node_or_rel_object, forced_fake_instance_class=None, additional_parameters=None):
        """
        This method build a fake instance from a node received from the Neo4j database.

        :param node_or_rel_object (required) : The Neo4j node object.

        :param forced_fake_instance_class (optional, default=None) : A class that will be forced as class of the fake instance. It is
                                                                     used for Relationship (or of one of its children class) instances.

        :param additional_parameters (optional, default=None) : It must be a dict that define additional parameters which ones will be
                                                                applied at the fake instance. It is used for the RelationshipInstance
                                                                (or of one of its children class) instances.

        :return: The fake instance.
        """

        fake_instance_class = cls

        if forced_fake_instance_class is not None:
            if BaseNodeAndRelationship in forced_fake_instance_class.__mro__\
                    or RelationshipInstance in forced_fake_instance_class.__mro__:
                fake_instance_class = forced_fake_instance_class

        fake_instance = FakeClass()
        fake_instance.__class__ = fake_instance_class

        property_dict = node_or_rel_object._properties

        for property_name, property_value in property_dict.items():
            setattr(fake_instance, property_name, property_value)

        # Add the 'labels' property to the fake_class_instance __dict__.
        if Node in fake_instance_class.__mro__:
            setattr(fake_instance, "labels", list(node_or_rel_object.labels))

        # Add the 'rel_type' property to the fake_class_instance __dict__.
        elif Relationship in fake_instance_class.__mro__ or RelationshipInstance in fake_instance_class.__mro__:
            setattr(fake_instance, "rel_type", node_or_rel_object.type)

        # Dynamically change the name of the RelationshipInstance object for a more visual render.
        if RelationshipInstance in fake_instance_class.__mro__:
            fake_instance.__class__.__name__ = f"{cls.__name__}Instance"

        # Add additional parameters.
        if additional_parameters is not None:
            if isinstance(additional_parameters, dict):
                for name, value in additional_parameters.items():
                    setattr(fake_instance, name, value)

            else:
                bulb_logger.error(
                    'BULBFakeInstanceError("The \'additional_parameters\' argument of the build_fake_instance() method, must be a dict.")')
                raise BULBFakeInstanceError(
                    "The 'additional_parameters' argument of the build_fake_instance() method, must be a dict.")

        return fake_instance


class Node(BaseNodeAndRelationship):
    """
    This is the base class for all Node classes.
    """

    def __init__(self, **received_properties_dict):
        self.labels = None
        self.properties = None
        self.properties_fields = None

        self.database_node_response = None

        self._constructor(received_properties_dict)

    def __getattribute__(self, item):
        value = super().__getattribute__(item)

        if Relationship in value.__class__.__mro__:
            value._self_node_instance = self
            value._name = item
        return value

    def __eq__(self, other):
        if self.uuid == other.uuid:
            return True
        return False

    def _constructor(self, received_properties_dict):
        """
        This method handle the construction of a node, it ensures a creation in the database and as a python instance.

        :param received_properties_dict (required) : The dictionary of values recovered during the instantiation of the node_model.
        """
        self.labels = self.__class__._get_labels()
        self.properties_fields = self.__class__._get_property_fields()
        self.properties = Property._build(self, received_properties_dict)

        database_node = DatabaseNode(current_object_labels_list=self.labels,
                                     current_object_properties_dict=self.properties,
                                     related_class_properties_fields_dict=self.properties_fields)

        self.returned_database_node_object = database_node.returned_node_object

    @classmethod
    def create(cls, **extrafields):
        new_instance = cls(**extrafields)
        return cls.build_fake_instance(new_instance.returned_database_node_object)

    @classmethod
    def get(cls, uuid=None, order_by=None, limit=None, skip=None, desc=False, only=None, filter=None, distinct=False,
            handmade=None, return_query=False):
        """
        This method allow the retrieving of Node (or of one of its children classes) instances.

        :param uuid (required): The Universal Unique Identifier of a node to get an unique instance.

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
                         ❌ : MATCH (n) RETURN n.first_name, n.last_name
                         ✅ : MATCH (n) RETURN n

                         In addition, note that the RETURN must absolutely be named 'n' like "node".

        :param return_query (optional, default=False) : Must be a boolean. If true, the method will return the cypher query.

        :return: If uuid is None, a list will be returned. Else it will be a unique instance.
        """

        if handmade is None:

            where_statement = ""
            uuid_property_statement = ""
            order_by_statement = ""
            limit_statement = ""
            skip_statement = ""
            desc_statement = ""

            # Build the uuid_property_statement.
            if uuid is not None:
                uuid_property_statement = "{uuid:'%s'}" % uuid

            # Build the match_statement.
            cyher_labels = DatabaseNode.format_labels_to_cypher(cls._get_labels())
            match_statement = f"MATCH (n:{cyher_labels} {uuid_property_statement})"

            # Build the where statement.
            if filter is not None:
                if not filter[0] != "n":
                    where_statement = "WHERE " + filter

                else:
                    where_statement = filter

            # Build the with_statement.
            with_statement = "WITH n"

            # Build order_by statements.
            if order_by is not None:
                order_by_statement = f"ORDER BY n.{order_by}"

            # Build return_statement statements.
            if not only:
                if not distinct:
                    return_statement = "RETURN (n)"

                else:
                    return_statement = "RETURN DISTINCT (n)"

            else:
                only_statement_list = []

                for element in only:
                    only_statement_list.append(f"n.{element}")

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

                        for node_object in response:
                            fake_instances_list.append(cls.build_fake_instance(node_object["n"],
                                                                               forced_fake_instance_class=cls))

                        if uuid is not None:
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
                fake_instances_list.append(cls.build_fake_instance(node_object["n"],
                                                                   forced_fake_instance_class=cls))

            return fake_instances_list


    @classmethod
    def get_str(cls, uuid=None, order_by=None, limit=None, skip=None, desc=False, only=None, filter=None, distinct=False,
            return_query=False):
        """
        A get method which returns string serialized instances / instances dict.

        See Node.get() documentation part to learn the role of each parameter.

        :return:
        """
        instances = cls.get(uuid=uuid, order_by=order_by, limit=limit, skip=skip, desc=desc, only=only, filter=filter,
                            distinct=distinct, return_query=return_query)

        if instances is not None:
            for instance in instances:

                if only is not None:
                    for property_name, property_value in instance.items():

                        # Serialize datetime, date and time objects.
                        if isinstance(property_value, neotime.DateTime) or isinstance(property_value, neotime.Date) or isinstance(property_value, neotime.Time):
                            instance[property_name] = str(property_value)

                else:
                    for property_name, property_value in instance.__dict__.items():

                        # Serialize datetime, date and time objects.
                        if isinstance(property_value, neotime.DateTime) or isinstance(property_value, neotime.Date) or isinstance(property_value, neotime.Time):
                            instance.__dict__[property_name] = str(property_value)

        return instances

    def update(self, property_name, new_property_value):
        class_name = self.__class__.__name__

        if not settings.BULB_CREATE_PROPERTY_IF_NOT_FOUND and property_name not in self.__dict__.keys():
            bulb_logger.warning(
                f'BULBNodeWarning("You are trying to update the property \'{property_name}\' of an {class_name} instance, but this property was not found in the instance dict. The update will have maybe no effect.")')
            warnings.warn(
                f"You are trying to update the property '{property_name}' of an {class_name} instance, but this property was not found in the instance dict. The update will have maybe no effect.",
                BULBNodeWarning)

        else:
            # Create property if it not exists.
            if property_name not in self.__dict__.keys():
                try:
                    gdbh.w_transaction("""
                    MATCH (n:%s {uuid:"%s"})
                    CALL apoc.create.setProperty(n, "%s", "%s") YIELD node
                    RETURN (n)
                    """ % (class_name, self.uuid,
                           property_name, None))

                    if eval(f"self.__class__.{property_name}.sftp"):
                        setattr(self, property_name, "None")
                    else:
                        setattr(self, property_name, None)

                except:
                    bulb_logger.warning(
                        f'BULBNodeWarning("You have defined BULB_CREATE_PROPERTY_IF_NOT_FOUND = True, but the neo4j\'s \'apoc\' plugin is not installed. So no new property was created.")')
                    warnings.warn(
                        f"You have defined BULB_CREATE_PROPERTY_IF_NOT_FOUND = True, but the neo4j's 'apoc' plugin is not installed. So no new property was created.",
                        BULBNodeWarning)

            # File handling (with SFTP storage).
            if eval(f"self.__class__.{property_name}.sftp"):

                old_remote_file_path_for_purge = None

                if self.__dict__[property_name] != "None" and self.__dict__[property_name] != "":
                    old_remote_file_path_for_purge = "/".join(self.__dict__[property_name].split("/")[3:])

                old_remote_file_path_for_remove = ("/www/" + old_remote_file_path_for_purge) if old_remote_file_path_for_purge is not None else None

                if not isinstance(new_property_value, InMemoryUploadedFile) and not isinstance(new_property_value, TemporaryUploadedFile):

                    if new_property_value == "None":

                        gdbh.w_transaction("""
                            MATCH (n:%s {uuid:'%s'})
                            WHERE exists(n.%s)
                            SET n.%s = "%s"
                        """ % (class_name, self.uuid,
                               property_name,
                               property_name, None))

                        # Remove the old file if there is one.
                        with SFTP.connect() as sftp:

                            if old_remote_file_path_for_remove is not None:
                                if sftp.exists(old_remote_file_path_for_remove):
                                    try:
                                        sftp.remove(old_remote_file_path_for_remove)

                                    except:
                                        pass

                                    if old_remote_file_path_for_purge is not None:
                                        if settings.BULB_USE_CDN77:
                                            from bulb.sftp_and_cdn.cdn_apis import CDN77

                                            try:
                                                CDN77.purge([old_remote_file_path_for_purge, ])

                                            except:
                                                pass

                    else:
                        bulb_logger(
                            f'BULBPropertyError("The property \'{property_name}\' is configured with \'sftp=True\' but its value is neither a file nor \'None\'.")')
                        raise BULBPropertyError(
                            f"The property '{property_name}' is configured with 'sftp=True' but its value is neither a file nor 'None'.")

                else:

                    temporary_local_file_path, remote_file_path = compress_file_and_build_paths(new_property_value)

                    with SFTP.connect() as sftp:
                        try:
                            sftp.put(temporary_local_file_path, remote_file_path)

                            if old_remote_file_path_for_remove is not None:
                                if sftp.exists(old_remote_file_path_for_remove):

                                    try:
                                        sftp.remove(old_remote_file_path_for_remove)

                                    except:
                                        pass

                                    if old_remote_file_path_for_purge is not None:
                                        if settings.BULB_USE_CDN77:
                                            from bulb.sftp_and_cdn.cdn_apis import CDN77

                                            try:
                                                CDN77.purge([old_remote_file_path_for_purge, ])

                                            except:
                                                pass

                        # Check and create default storage folders if they are not already created.
                        except IOError:
                            if not sftp.exists("/www/staticfiles"):
                                sftp.mkdir("/www/staticfiles")

                            if not sftp.exists("/www/staticfiles/content"):
                                sftp.mkdir("/www/staticfiles/content")

                            if not sftp.exists("/www/staticfiles/content/img"):
                                sftp.mkdir("/www/staticfiles/content/img")

                            if not sftp.exists("/www/staticfiles/content/pdf"):
                                sftp.mkdir("/www/staticfiles/content/pdf")

                            if not sftp.exists("/www/staticfiles/content/svg"):
                                sftp.mkdir("/www/staticfiles/content/svg")

                            sftp.put(temporary_local_file_path, remote_file_path)

                            if old_remote_file_path_for_remove is not None:
                                if sftp.exists(old_remote_file_path_for_remove):

                                    try:
                                        sftp.remove(old_remote_file_path_for_remove)

                                    except:
                                        pass

                                    if old_remote_file_path_for_purge is not None:
                                        if settings.BULB_USE_CDN77:
                                            from bulb.sftp_and_cdn.cdn_apis import CDN77

                                            try:
                                                CDN77.purge([old_remote_file_path_for_purge, ])

                                            except:
                                                pass

                    os.remove(temporary_local_file_path)

                    full_stored_file_path_list = (settings.BULB_SFTP_PULL_URL + remote_file_path).split("/")
                    full_stored_file_path_list.pop(3)
                    full_stored_file_path = "/".join(full_stored_file_path_list)

                    gdbh.w_transaction("""
                    MATCH (n:%s {uuid:"%s"})
                    WHERE exists(n.%s)
                    SET n.%s = "%s"
                    """ % (class_name, self.uuid,
                           property_name,
                           property_name, full_stored_file_path))

                    new_property_value = full_stored_file_path

            # Integer, float, boolean and list handling.
            elif isinstance(new_property_value, int) or isinstance(new_property_value, float) or isinstance(new_property_value, bool) or isinstance(new_property_value, list):
                gdbh.w_transaction("""
                MATCH (n:%s {uuid:"%s"})
                WHERE exists(n.%s)
                SET n.%s = %s
                """ % (class_name, self.uuid,
                       property_name,
                       property_name, new_property_value))

            # Datetime handling.
            elif isinstance(new_property_value, datetime.datetime):
                gdbh.w_transaction("""
                            MATCH (n:%s {uuid:"%s"})
                            WHERE exists(n.%s)
                            SET n.%s = datetime("%s")
                            """ % (class_name, self.uuid,
                                   property_name,
                                   property_name, str(new_property_value).replace(" ", "T")))

            # Date handling.
            elif isinstance(new_property_value, datetime.date):
                gdbh.w_transaction("""
                                MATCH (n:%s {uuid:"%s"})
                                WHERE exists(n.%s)
                                SET n.%s = date("%s")
                                """ % (class_name, self.uuid,
                                       property_name,
                                       property_name, str(new_property_value)))

            # Time handling.
            elif isinstance(new_property_value, datetime.time):
                gdbh.w_transaction("""
                            MATCH (n:%s {uuid:"%s"})
                            WHERE exists(n.%s)
                            SET n.%s = time("%s")
                            """ % (class_name, self.uuid,
                                   property_name,
                                   property_name, str(new_property_value)))

            # String handling.
            elif isinstance(new_property_value, str):
                # Escape quotes to prevent cypher syntax errors.
                new_property_value = new_property_value.replace('"', '\\"').replace("'", "\\'")

                gdbh.w_transaction("""
                MATCH (n:%s {uuid:'%s'})
                WHERE exists(n.%s)
                SET n.%s = "%s"
                """ % (class_name, self.uuid,
                       property_name,
                       property_name, new_property_value))

            # Other
            else:
                gdbh.w_transaction("""
                MATCH (n:%s {uuid:'%s'})
                WHERE exists(n.%s)
                SET n.%s = "%s"
                """ % (class_name, self.uuid,
                       property_name,
                       property_name, new_property_value))

            setattr(self, property_name, new_property_value)

    def delete(self):

        # Handle sftp files removing.
        # All the attributes (representing the properties of the Node) of the current node class.
        class_properties_dict = self.__class__._get_property_fields()

        for field_name, field_content in class_properties_dict.items():

            if eval(f"self.__class__.{field_name}.sftp"):

                old_remote_file_path_for_purge = None

                if self.__dict__[field_name] != "None" and self.__dict__[field_name] != "":
                    old_remote_file_path_for_purge = "/".join(self.__dict__[field_name].split("/")[3:])

                old_remote_file_path_for_remove = ("/www/" + old_remote_file_path_for_purge) if old_remote_file_path_for_purge is not None else None

                # Remove the old file if there is one.
                with SFTP.connect() as sftp:

                    if old_remote_file_path_for_remove is not None:
                        if sftp.exists(old_remote_file_path_for_remove):
                            try:
                                sftp.remove(old_remote_file_path_for_remove)

                            except:
                                pass

                            if old_remote_file_path_for_purge is not None:
                                if settings.BULB_USE_CDN77:
                                    from bulb.sftp_and_cdn.cdn_apis import CDN77

                                    try:
                                        CDN77.purge([old_remote_file_path_for_purge, ])

                                    except:
                                        pass

        # Handle relationships on_delete behaviours.
        class_relationships_dict = self._get_relationship_fields()

        """
        ################################################################################################################
        ######################################### THE BELOW CODE IS NOT TESTED #########################################
        ################################################################################################################
        """
        # Handle sftp files removing.
        for relationship_name, relationship in class_relationships_dict.items():

            additional_properties = None
            if relationship.properties is not None:
                additional_properties = relationship.properties

            relationship_properties = relationship._get_property_fields(additional_fields_dict=additional_properties)

            for field_name, field_value in relationship_properties.items():

                # if eval(f"field_value.__class__.{field_name}.sftp"):
                if field_value.sftp:

                    old_remote_file_path_for_purge = None

                    if field_value.__dict__[field_name] != "None" and field_value.__dict__[field_name] != "":
                        old_remote_file_path_for_purge = "/".join(field_value.__dict__[field_name].split("/")[3:])

                    old_remote_file_path_for_remove = ("/www/" + old_remote_file_path_for_purge) if old_remote_file_path_for_purge is not None else None

                    # Remove the old file if there is one.
                    with SFTP.connect() as sftp:

                        if old_remote_file_path_for_remove is not None:
                            if sftp.exists(old_remote_file_path_for_remove):
                                try:
                                    sftp.remove(old_remote_file_path_for_remove)

                                except:
                                    pass

                                if old_remote_file_path_for_purge is not None:
                                    if settings.BULB_USE_CDN77:
                                        from bulb.sftp_and_cdn.cdn_apis import CDN77

                                        try:
                                            CDN77.purge([old_remote_file_path_for_purge, ])

                                        except:
                                            pass
        """
        ################################################################################################################
        ######################################### THE ABOVE CODE IS NOT TESTED #########################################
        ################################################################################################################
        """

        for relationship_field_name, relationship_field in class_relationships_dict.items():
            if relationship_field.on_delete == "PROTECT":
                gdbh.w_transaction("""
                MATCH (n:%s {uuid:'%s'})
                DETACH DELETE (n)
                """ % (self.__class__.__name__, self.uuid))

            elif relationship_field.on_delete == "CASCADE":
                related_nodes = eval(f"self.{relationship_field_name}.get()")

                gdbh.w_transaction("""
                MATCH (n:%s {uuid:'%s'})
                DETACH DELETE (n)
                """ % (self.__class__.__name__, self.uuid))

                if related_nodes is not None:
                    for node in related_nodes:
                        node.delete()

    @classmethod
    def count(cls, uuid=None, order_by=None, limit=None, skip=None, desc=False, only=None, filter=None, distinct=False, handmade=None,
              **extrafields):
        request_statement = cls.get(uuid=uuid, order_by=order_by, limit=limit, skip=skip, desc=desc, only=only, filter=filter,
                                    handmade=handmade, return_query=True, **extrafields)
        request_count_statement = None

        if not distinct:
            request_count_statement = request_statement.split("RETURN")[0] + "RETURN COUNT(n)"

        else:
            request_count_statement = request_statement.split("RETURN")[0] + "RETURN COUNT(DISTINCT n)"

        response = gdbh.r_transaction(request_count_statement)

        if not distinct:
            return response[0]["COUNT(n)"]

        else:
            return response[0]["COUNT(DISTINCT n)"]

    @classmethod
    def _get_labels(cls):
        """
        This method detects and regroups in a list, all labels of a Node instance. Then, it returns the list.
        :return: A list of all Node instance's labels.
        """
        # Prevent duplication with a set.
        labels_list = set()

        classes_dicts = []

        # Add the dict of the current class and those of these parents.
        for mro_class in cls.__mro__:
            classes_dicts.append(mro_class.__dict__)

        # Retrieve labels values of each class dict.
        for class_dict in classes_dicts:
            for key, value in class_dict.items():
                if str(key) == 'labels':
                    if isinstance(value, list):
                        for label in value:
                            labels_list.add(label)

                    elif isinstance(value, str):
                        labels_list.add(value)

        # Add classes names in the labels list.
        for mro_class in cls.__mro__:
            if not mro_class in [object, Node, BaseNodeAndRelationship]:
                labels_list.add(mro_class.__name__)

        return list(labels_list)

    @classmethod
    def _get_relationship_fields(cls):
        """
        This method detects and regroups in a dictionary, all relationship fields of a Node instance. Then, it returns
        the dictionary.
        :return: A dictionary of all Node instance's relationships.
        """
        relationships_dict = {}

        # Retrieve the relationships declared in the class and those declared in all these parents: allow class inheritance.
        class_dict = cls.__dict__.copy()
        for mro_class in cls.__mro__:
            class_dict.update(mro_class.__dict__)

        for k, v in class_dict.items():
            if isinstance(v, Relationship) or Relationship in v.__class__.__mro__:
                relationships_dict[k] = v

        return relationships_dict


class Relationship(BaseNodeAndRelationship):
    """
    This class allow using of relationships with node_models.

    :param rel_type (required) : This parameter defines the relationship type. It must be a string.
                                 See : https://neo4j.com/docs/getting-started/current/graphdb-concepts/#graphdb-relationship-types

    :param direction (optional, default="from") : Must be "from", "to", or "bi". If it is "from", the relationship will be an arrow that
                                                  starts from the self node_model's instance to other node_models' instances.
                                                  If it is "to" it will be the reverse case : the relationship will be an arrow that
                                                  starts from other node_models' instances to the self node_model's instance.
                                                  Finally if it is "bi", it will be two relationships that will work by peers, one from
                                                  and one to the self node_model's instance : a bi-directional relationships will be
                                                  created.
                                                  Default value "from".

    :param properties_fields (optional, default=None) : A dict of properties for "all in node_model" syntax. If the Relationship
                                                        classes are out of the node_model classes, this argument will be None.


    :param start (optional, default=None) : This parameter must be a node_model class, its name or "self".
                                            It applies a start constraint to the relationship.

    :param target (optional, default=None) : This parameter must be a node_model class, its name or "self".
                                             It applies a target constraint to the relationship.

    :param auto (optional, default=False) : This parameter must be a boolean. If it is True, the relationship is allowed to be applied
                                            on one unique node, which one will be the start and the target of the relationship.
                                            The default value is False.

    :param on_delete (optional, default="PROTECT") : This parameter must be "PROTECT" or "CASCADE". It defines the behavior of the
                                                     related nodes. If it is "PROTECT", if the self node object of the relationship is
                                                     deleted, nothing happen for nodes related to it (A simple DETACH DELETE command is
                                                     run). In the other hand, if it is "CASCADE", the other nodes will be deleted in the
                                                     same time as the self node object. The default value is "PROTECT".

    :param unique (optional, default=False) : This parameter must be a boolean. If it is True the relationship will be unique.

    """

    def __init__(self, rel_type=None, properties_fields=None, direction=None, start=None, target=None, auto=None,
                 on_delete=None, unique=None):
        # Foundamentals.
        self.rel_type = rel_type
        self.properties = None
        self.properties_fields = properties_fields

        # Optionals.
        self.direction = direction
        self.start = start
        self.target = target
        self.auto = auto
        self.on_delete = on_delete
        self.unique = unique

        # Internals.
        self._self_node_instance = None
        self._name = None

        self.manage_is_done = False

    def _manage_relationship_parameters(self):
        """
        This method manage all the Relationship object's parameters : It check their values and assigns them default
        values if nothing is found. More, it allow the "distinct" syntax for relationships.
        :return:
        """
        all_node_models = get_all_node_models()

        # 'rel_type' parameter value research.
        if self.rel_type is None:
            try:
                # Support the 'distinct' syntax.
                self.rel_type = self.__class__.rel_type

            except AttributeError:
                bulb_logger.error(f'BULBRelationshipError("A {self.__class__.__name__} instance must have a \'rel_type\'.")')
                raise BULBRelationshipError(f"A {self.__class__.__name__} instance must have a 'rel_type'.")

        # 'rel_type' parameter value check.
        if not isinstance(self.rel_type, str):
            bulb_logger.error(
                f'BULBRelationshipError("The \'rel_type\' argument of a {self.__class__.__name__} instance must be a string.")')
            raise BULBRelationshipError(
                f"The 'rel_type' argument of a {self.__class__.__name__} instance must be a string.")

        # 'direction' parameter value research.
        if self.direction is None:
            try:
                # Support the 'distinct' syntax.
                self.direction = self.__class__.direction

            except AttributeError:
                self.direction = "from"

        # 'direction' parameter value check.
        if self.direction not in ["from", "to", "bi"]:
            bulb_logger.error(
                'BULBRelationshipError("The parameter \'direction\' of a Relationship must be a \'from\', \'to\' or \'bi\'.")')
            raise BULBRelationshipError(
                "The parameter 'direction' of a Relationship must be a 'from', 'to' or 'bi'.")

        # 'start' parameter value research.
        if self.start is None:
            try:
                # Support the 'distinct' syntax.
                self.start = self.__class__.start

            except AttributeError:
                pass

        # 'start' parameter value check.
        if self.start is not None:
            if self.direction == "from" or self.direction == "bi":
                if not self.start == "self":
                    bulb_logger.error(
                        f'BULBRelationshipError("A {self.__class__.__name__} instance must have start = \'self\' if direction = \'from\' or \'bi\'.")')
                    raise BULBRelationshipError(
                        f"A {self.__class__.__name__} instance must have start = 'self' if direction = 'from' or 'bi'.")

            else:
                # Support class syntax.
                if inspect.isclass(self.start):
                    if not Node in self.start.__mro__:
                        bulb_logger.error(
                            f'BULBRelationshipError("The parameter \'start\' of a {self.__class__.__name__} instance must be a node_model, its name or \'self\'.")')
                        raise BULBRelationshipError(
                            f"The parameter 'start' of a {self.__class__.__name__} instance must be a node_model, its name or 'self'.")

                # Support string syntax.
                elif isinstance(self.start, str):
                    if self.start == "self":
                        pass

                    else:
                        related_node_model_was_found = False
                        for node_model in all_node_models:
                            if self.start == "User":
                                from bulb.contrib.auth.node_models import User
                                self.start = User
                                related_node_model_was_found = True

                            elif self.start == "Group":
                                from bulb.contrib.auth.node_models import Group
                                self.start = Group
                                related_node_model_was_found = True

                            elif self.start == "Permission":
                                from bulb.contrib.auth.node_models import Permission
                                self.start = Permission
                                related_node_model_was_found = True

                            elif self.start == "Session":
                                from bulb.contrib.sessions.node_models import Session
                                self.start = Session
                                related_node_model_was_found = True

                            elif node_model.__name__ == self.start:
                                self.start = node_model
                                related_node_model_was_found = True
                                break

                        if related_node_model_was_found is False:
                            bulb_logger.error(
                                f'BULBRelationshipError("The parameter \'start\' of a {self.__class__.__name__} instance must be a node_model, its name or \'self\'.")')
                            raise BULBRelationshipError(
                                f"The parameter 'start' of a {self.__class__.__name__} instance must be a node_model, its name or 'self'.")

                else:
                    bulb_logger.error(
                        f'BULBRelationshipError("The parameter \'start\' of a {self.__class__.__name__} instance must be a node_model, its name or \'self\'.")')
                    raise BULBRelationshipError(
                        f"The parameter 'start' of a {self.__class__.__name__} instance must be a node_model, its name or 'self'.")

        # 'target' parameter value research.
        if self.target is None:
            try:
                # Support the 'distinct' syntax.
                self.target = self.__class__.target

            except AttributeError:
                pass

        # 'target' parameter value check.
        if self.target is not None:
            if self.direction == "to":
                if not self.target == "self":
                    bulb_logger.error(
                        f'BULBRelationshipError("A {self.__class__.__name__} instance must have target = \'self\' if direction = \'to\'.")')
                    raise BULBRelationshipError(
                        f"A {self.__class__.__name__} instance must have target = 'self' if direction = 'to'.")

            else:
                # Support class syntax.
                if inspect.isclass(self.target):
                    if not Node in self.target.__mro__:
                        bulb_logger.error(
                            f'BULBRelationshipError("The parameter \'target\' of a {self.__class__.__name__} instance must be a node_model, its name or \'self\'.")')
                        raise BULBRelationshipError(
                            f"The parameter 'target' of a {self.__class__.__name__} instance must be a node_model, its name or 'self'.")

                # Support string syntax.
                elif isinstance(self.target, str):
                    if self.target == "self":
                        pass

                    else:
                        related_node_model_was_found = False
                        for node_model in all_node_models:
                            if node_model.__name__ == self.target:
                                self.target = node_model
                                related_node_model_was_found = True
                                break

                        if related_node_model_was_found is False:
                            bulb_logger.error(
                                f'BULBRelationshipError("The parameter \'target\' of a {self.__class__.__name__} instance must be a node_model, its name or \'self\'.")')
                            raise BULBRelationshipError(
                                f"The parameter 'target' of a {self.__class__.__name__} instance must be a node_model, its name or 'self'.")

                else:
                    bulb_logger.error(
                        f'BULBRelationshipError("The parameter \'target\' of a {self.__class__.__name__} instance must be a node_model, its name or \'self\'.")')
                    raise BULBRelationshipError(
                        f"The parameter 'target' of a {self.__class__.__name__} instance must be a node_model, its name or 'self'.")

        # 'auto' parameter value research and default value assignement.
        if self.auto is None:
            try:
                # Support the 'distinct' syntax.
                self.auto = self.__class__.auto

            except AttributeError:
                self.auto = False

        # 'auto' parameter value check.
        if self.auto is not None:
            if not isinstance(self.auto, bool):
                bulb_logger.error(
                    f'BULBRelationshipError("The parameter \'auto\' of a {self.__class__.__name__} instance must be a boolean.")')
                raise BULBRelationshipError(
                    f"The parameter 'auto' of a {self.__class__.__name__} instance must be a boolean.")

        # 'on_delete' parameter value research and default value assignement.
        if self.on_delete is None:
            try:
                # Support the 'distinct' syntax.
                self.on_delete = self.__class__.on_delete

            except AttributeError:
                self.on_delete = "PROTECT"

        # 'on_delete' parameter value check.
        if self.on_delete is not None:
            if not self.on_delete in ["PROTECT", "CASCADE"]:
                bulb_logger.error(
                    f'BULBRelationshipError("The parameter \'on_delete\' of a {self.__class__.__name__} instance must be \'PROTECT\' or \'CASCADE\'.")')
                raise BULBRelationshipError(
                    f"The parameter 'on_delete' of a {self.__class__.__name__} instance must be 'PROTECT' or 'CASCADE'.")

        # 'unique' parameter value research and default value assignement.
        if self.unique is None:
            try:
                # Support the 'distinct' syntax.
                self.unique = self.__class__.unique

            except AttributeError:
                self.unique = False

        # 'unique' parameter value check.
        if self.unique is not None:
            if not isinstance(self.unique, bool):
                bulb_logger.error(
                    f'BULBRelationshipError("The parameter \'unique\' of a {self.__class__.__name__} instance must be a boolean.")')
                raise BULBRelationshipError(
                    f"The parameter 'unique' of a {self.__class__.__name__} instance must be a boolean.")

    def _constructor(self, received_properties_dict):
        """
        This method collects and assigns to the current Relationship (or of one of its children classes) instance, all
        the required datas for relationship creation.

        :param received_properties_dict: The dictionary of values recovered during the instantiation of the Relationship
                                         class or of one of its children.
        """
        if self.manage_is_done is False:
            self._manage_relationship_parameters()
            self.manage_is_done = True

        if self.properties_fields is not None:
            self.properties_fields = self._get_property_fields(additional_fields_dict=self.properties_fields)

        else:
            self.properties_fields = self._get_property_fields()

        self.properties = Property._build(self, received_properties_dict)

    def add(self, instance=None, uuid=None, properties=None):
        """
        This method handle the creation of the relationship between the self_instance, contained in the self._from
        attribute, and the other_instance, retrieved as parameter of its method.

        :param instance (required if the uuid is'nt gived) : A node_model's instance, to which the relationship will target.

        :param uuid (required if the instance is'nt gived) : A node_models uuid, to which the relationship will target.

        :param properties (optional, default=None): The properties dictionary to fill if the relationship take one or more properties.

        :return: A RelationshipInstance instance, or a dict of two RelationshipInstance instances if self.bi (bidirectional
                 relationship) is True.
        """
        if self.manage_is_done is False:
            self._manage_relationship_parameters()
            self.manage_is_done = True

        received_properties_dict = (properties if properties is not None else {})
        relationship_start_node = None
        relationship_target_node = None
        self_node_instance = self._self_node_instance
        other_node_instance = None

        if instance is not None:

            # Get the two instance of the relationships.
            other_node_instance = instance

            # Define the two nodes of the relationships and apply 'direction', 'start' and 'target' constraints.
            if self.direction == "from" or self.direction == "bi":
                relationship_start_node = self_node_instance

                if self.target is not None:

                    if self.target in other_node_instance.__class__.__mro__ or self.target.__name__ == other_node_instance.__class__.__name__:
                        relationship_target_node = other_node_instance

                    else:
                        bulb_logger.error(
                            f'BULBRelationshipError("The \'{self._name}\' relationship connects \'{relationship_start_node.__class__.__name__}\' to \'{self.target.__name__}\' instances (or instances of one of their children classes). Not \'{relationship_start_node.__class__.__name__}\' to \'{other_node_instance.__class__.__name__}\'.")')
                        raise BULBRelationshipError(
                            f"The '{self._name}' relationship connects '{relationship_start_node.__class__.__name__}' to '{self.target.__name__}' instances (or instances of one of their children classes). Not '{relationship_start_node.__class__.__name__}' to '{other_node_instance.__class__.__name__}'.")

                else:
                    if Node in other_node_instance.__class__.__mro__:
                        relationship_target_node = other_node_instance

                    else:
                        bulb_logger.error(
                            f'BULBRelationshipError("The \'instance\' parameter of the add() method of {self.__class__.__name__} instances must be a node_model\'s instance.")')
                        raise BULBRelationshipError(
                            f"The 'instance' parameter of the add() method of {self.__class__.__name__} instances must be a node_model's instance.")

            elif self.direction == "to":
                relationship_target_node = self_node_instance

                if self.start is not None:

                    if self.start in other_node_instance.__class__.__mro__ or self.start.__name__ == other_node_instance.__class__.__name__:
                        relationship_start_node = other_node_instance

                    else:
                        bulb_logger.error(
                            f'BULBRelationshipError("The \'{self._name}\' relationship connects \'{self.start.__name__}\' to \'{relationship_target_node.__class__.__name__}\' instances (or instances of one of their children classes). Not \'{other_node_instance.__class__.__name__}\' to \'{relationship_target_node.__class__.__name__}\'.")')
                        raise BULBRelationshipError(
                            f"The '{self._name}' relationship connects '{self.start.__name__}' to '{relationship_target_node.__class__.__name__}' instances (or instances of one of their children classes). Not '{other_node_instance.__class__.__name__}' to '{relationship_target_node.__class__.__name__}'.")

                else:
                    if Node in other_node_instance.__class__.__mro__:
                        relationship_start_node = other_node_instance

                    else:
                        bulb_logger.error(
                            f'BULBRelationshipError("The \'instance\' parameter of the add() method of {self.__class__.__name__} instances must be a node_model\'s instance.")')
                        raise BULBRelationshipError(
                            f"The 'instance' parameter of the add() method of {self.__class__.__name__} instances must be a node_model's instance.")

        elif uuid is not None:
            # Get the two instance of the relationships.
            other_node_instance = FakeClass()
            other_node_instance.uuid = uuid

            # Define the two nodes of the relationships and apply 'direction', 'start' and 'target' constraints.
            if self.direction == "from" or self.direction == "bi":
                relationship_start_node = self_node_instance

                if self.target is not None:
                    response = gdbh.r_transaction("""
                    MATCH (n:%s {uuid:'%s'})
                    RETURN count(n) > 0 as bool
                    """ % (self.target.__name__, uuid))

                    if response[0]["bool"] is True:
                        other_node_instance.__class__.__name__ = self.target.__name__
                        relationship_target_node = other_node_instance

                    else:
                        bulb_logger.error(
                            f'BULBRelationshipError("The \'{self._name}\' relationship connects \'{relationship_start_node.__class__.__name__}\' to \'{self.target.__name__}\' instances (or instances of one of their children classes) only.")')
                        raise BULBRelationshipError(
                            f"The '{self._name}' relationship connects '{relationship_start_node.__class__.__name__}' to '{self.target.__name__}' instances (or instances of one of their children classes) only.")

                else:
                    response = gdbh.r_transaction("""
                    MATCH (n: {uuid:'%s'})
                    RETURN count(n) > 0 as bool, LABELS(n) as labels
                    """ % uuid)

                    if response[0]["bool"] is True:
                        other_node_instance.__class__.__name__ = response[0]["labels"][0]
                        relationship_target_node = other_node_instance

            elif self.direction == "to":
                relationship_target_node = self_node_instance

                if self.start is not None:
                    response = gdbh.r_transaction("""
                    MATCH (n:%s {uuid:'%s'})
                    RETURN count(n) > 0 as bool
                    """ % (self.start.__name__, uuid))

                    if response[0]["bool"] is True:
                        other_node_instance.__class__.__name__ = self.start.__name__
                        relationship_start_node = other_node_instance

                    else:
                        bulb_logger.error(
                            f'BULBRelationshipError("The \'{self._name}\' relationship connects \'{self.start.__name__}\' to \'{relationship_target_node.__class__.__name__}\' instances (or instances of one of their children classes) only.")')
                        raise BULBRelationshipError(
                            f"The '{self._name}' relationship connects '{self.start.__name__}' to '{relationship_target_node.__class__.__name__}' instances (or instances of one of their children classes) only.")

                else:
                    response = gdbh.r_transaction("""
                    MATCH (n: {uuid:'%s'})
                    RETURN count(n) > 0 as bool, LABELS(n) as labels
                    """ % uuid)

                    if response[0]["bool"] is True:
                        other_node_instance.__class__.__name__ = response[0]["labels"][0]
                        relationship_start_node = other_node_instance

        else:
            bulb_logger.error(
                f'BULBRelationshipError("The add() method of {self.__class__.__name__} instances must take either an \'uuid\' or a node_model instance.")')
            raise BULBRelationshipError(
                f"The add() method of {self.__class__.__name__} instances must take either an 'uuid' or a node_model instance.")

        # Apply the 'auto' constraint.
        if self.auto is False:
            if relationship_start_node.uuid == relationship_target_node.uuid:
                bulb_logger.error(
                    f'BULBRelationshipError("The parameter \'auto\' of the \'{self._name}\' relationship is True. It says that the same node cannot be the start and the target of a relationship.")')
                raise BULBRelationshipError(
                    f"The parameter 'auto' of the '{self._name}' relationship is True. It says that the same node cannot be the start and the target of a relationship.")

        # Build properties.
        self._constructor(received_properties_dict)

        relationship_cypher_properties = DatabaseNode.format_properties_to_cypher(self.properties_fields,
                                                                                  self.properties)
        response = None

        if self.direction == "from":

            # Apply the 'unique' constraint.
            if self.unique:
                uniqueness_test_response = gdbh.r_transaction("""
                           MATCH (n:%s {uuid:'%s'}),
                                 (n)-[r:%s]->()
                           RETURN (r)
                           """ % (relationship_start_node.__class__.__name__, relationship_start_node.uuid,
                                  self.rel_type))

                if uniqueness_test_response:
                    bulb_logger.error(
                        f'BULBUniqueConstraintError("The {self.__class__.__name__} instances must be UNIQUE : {self_node_instance.__class__.__name__} instances must have an unique \'{self._name}\'.")')
                    raise BULBUniqueConstraintError(
                        f"The {self.__class__.__name__} instances must be UNIQUE : {self_node_instance.__class__.__name__} instances must have an unique '{self._name}'.")

            response = gdbh.w_transaction("""
                       MATCH (n1:%s {uuid:'%s'}),
                             (n2:%s {uuid:'%s'})
                       CREATE (n1)-[r:%s %s]->(n2)
                       RETURN (r)
                       """ % (relationship_start_node.__class__.__name__, relationship_start_node.uuid,
                              relationship_target_node.__class__.__name__, relationship_target_node.uuid,
                              self.rel_type, relationship_cypher_properties))

            return self.__class__.build_fake_instance(response[0]["r"])

        elif self.direction == "to":

            # Apply the 'unique' constraint.
            if self.unique:
                uniqueness_test_response = gdbh.r_transaction("""
                           MATCH (n:%s {uuid:'%s'}),
                                 ()-[r:%s]->(n)
                           RETURN (r)
                           """ % (relationship_target_node.__class__.__name__, relationship_target_node.uuid,
                                  self.rel_type))

                if uniqueness_test_response:
                    bulb_logger.error(
                        f'BULBUniqueConstraintError("The {self.__class__.__name__} instances must be UNIQUE : {self_node_instance.__class__.__name__} instances must have an unique \'{self._name}\'.")')
                    raise BULBUniqueConstraintError(
                        f"The {self.__class__.__name__} instances must be UNIQUE : {self_node_instance.__class__.__name__} instances must have an unique '{self._name}'.")

            response = gdbh.w_transaction("""
                       MATCH (n1:%s {uuid:'%s'}),
                             (n2:%s {uuid:'%s'})
                       CREATE (n1)-[r:%s %s]->(n2)
                       RETURN (r)
                       """ % (relationship_start_node.__class__.__name__, relationship_start_node.uuid,
                              relationship_target_node.__class__.__name__, relationship_target_node.uuid,
                              self.rel_type, relationship_cypher_properties))

            return self.__class__.build_fake_instance(response[0]["r"])

        elif self.direction == "bi":

            # Apply the 'unique' constraint.
            if self.unique:
                uniqueness_test_response = gdbh.r_transaction("""
                           MATCH (n:%s {uuid:'%s'}),
                                 (n)-[r_from:%s]->(),
                                 (n)<-[r_to:%s]-()
                           RETURN r_from, r_to
                           """ % (relationship_start_node.__class__.__name__, relationship_start_node.uuid,
                                  self.rel_type,
                                  self.rel_type))

                if uniqueness_test_response:
                    bulb_logger.error(
                        f'BULBUniqueConstraintError("The {self.__class__.__name__} instances must be UNIQUE : {self_node_instance.__class__.__name__} instances must have an unique \'{self._name}\'.")')
                    raise BULBUniqueConstraintError(
                        f"The {self.__class__.__name__} instances must be UNIQUE : {self_node_instance.__class__.__name__} instances must have an unique '{self._name}'.")

            # Note : Both relationships are create from the same datas, but the uuid of the 'to' relationship is
            #        changed to prevent uuid's concept violation.
            response = gdbh.w_transaction("""
                       MATCH (n1:%s {uuid:'%s'}),
                             (n2:%s {uuid:'%s'})
                       CREATE (n1)-[r_from:%s %s]->(n2),
                              (n1)<-[r_to:%s %s]-(n2)
                       SET r_to.uuid = '%s'
                       RETURN r_from, r_to
                       """ % (relationship_start_node.__class__.__name__, relationship_start_node.uuid,
                              relationship_target_node.__class__.__name__, relationship_target_node.uuid,
                              self.rel_type, relationship_cypher_properties,
                              self.rel_type, relationship_cypher_properties,
                              make_uuid()))

            return {'rel_from_self': self.__class__.build_fake_instance(response[0]["r_from"]),
                    'rel_to_self': self.__class__.build_fake_instance(response[0]["r_to"])}

    def get(self, direction="bi", returned="node", order_by=None, limit=None,  skip=None, desc=False, distinct=False,
            only=None, filter=None, return_query=False):
        """
        This method allow the retrieving of node_models' instances' relationships but also of the other node_models'
        instances on the other ends of these relationships.

        :param direction (optional, default="bi") : Must be "from", "to", or "bi". If it is "from", the research will be focused on
                                                    all the relationships that have as start point the self node_model's instance. If
                                                    it is "to", the research will be focused on all the relationships that have as end
                                                    point the self node_model's instance. Finally, if it is "bi", the research will be
                                                    focused on the relationships of both cases.

        :param returned (optional, default="node") : Must be "rel", "node" or "both". If it is "rel", the method will return a list
                                                     that contains relationships as RelationshipInstance (or of one of its children
                                                     classes) instances. If it is "node", the method will return a list that contains
                                                     the nodes at the other ends of these relationships as node_models' instances.
                                                     Finally if it is "both", it will return a list of dictionaries in which ones the
                                                     "rel" key refers to a relationships and the "node" key to its associated node.
                                                     Example : {"rel": <RelationshipInstance object(uuid="3a43238c76ec4d6cb392b138f0871e75")>,
                                                                "node": <Human object(uuid="ec04770e5c8b428d9d94678c3666d312")>}

        :param order_by (optional, default=None) : Must be the name of the property with which the returned datas will be sorted. BUT,
                                                   if self.returned = "both", two different types of datas will be returned
                                                   (relationships and nodes).
                                                   So to sort them this property must start with "r." (like 'relationships') or "n."
                                                   (like 'nodes').
                                                   Examples : "r.datetime", "n.first_name", etc...

        :param limit (optional, default=None) : Must be an integer. This parameter defines the number of returned elements.

        :param skip (optional, default=None) : Must be an integer. This parameter defines the number of skipped elements. For example
                                               if self.skip = 3, the 3 first returned elements will be skipped.

        :param desc (optional, default=False) : Must be a boolean. If it is False the elements will be returned in an increasing order,
                                                but it is True, they will be returned in a descending order.

        :param distinct (optional, default=False) : Must be a boolean. If it is True, the returned list will be only composed with
                                                    unique elements.

        :param only (optional, default=None) : Must be a list of field_names. If this parameter is filled, the return will not be
                                               node_models and relationships instances, but a dict with "only" the mentioned fields.
                                               BUT, if self.returned = "both", two different types of datas will be returned
                                               (relationships and nodes).
                                               So to mention their properties fields, the elements of the list will must start with
                                               "r." (like 'relationships') or "n." (like 'nodes').
                                               Examples : "r.datetime", "n.first_name", etc...

        :param filter (optional, default=None) : Must be Q statement. You must use the Q class stored in bulb.db
                                                 Example: Q(name__contains="al") | Q(age__year__lte=8)

        :param return_query (optional, default=False) : Must be a boolean. If true, the method will return the cypher query.

        :return: (see :param returned)
        """
        if self.manage_is_done is False:
            self._manage_relationship_parameters()
            self.manage_is_done = True

        request_required_values_list = []
        self_node_instance = self._self_node_instance

        match_statement = None
        where_statement = ""
        with_statement = None
        order_by_statement = ""
        limit_statement = ""
        skip_statement = ""
        desc_statement = ""
        return_statement = None

        # Find start and target labels.
        start_labels = ""
        target_labels = ""

        if inspect.isclass(self.start):
            start_labels = ":" + self.start.__name__

        elif isinstance(self.start, str):
            start_labels = ":" + self.start

        if inspect.isclass(self.target):
            target_labels = ":" + self.target.__name__

        elif isinstance(self.target, str):
            target_labels = ":" + self.target

        # Build the match_statement.
        if direction == "from":

            if self.direction == "from" or self.direction == "bi":
                if self.target:
                    match_statement = "MATCH (:%s {uuid:'%s'})-[r:%s]->" + "(n%s)" % target_labels

                else:
                    match_statement = "MATCH (:%s {uuid:'%s'})-[r:%s]->(n)"

            elif self.direction == "to":
                if self.start:
                    match_statement = "MATCH (:%s {uuid:'%s'})-[r:%s]->" + "(n%s)" % start_labels

                else:
                    match_statement = "MATCH (:%s {uuid:'%s'})-[r:%s]->(n)"

        elif direction == "to":

            if self.direction == "from" or self.direction == "bi":
                if self.target:
                    match_statement = "MATCH (:%s {uuid:'%s'})<-[r:%s]-" + "(n%s)" % target_labels

                else:
                    match_statement = "MATCH (:%s {uuid:'%s'})<-[r:%s]-(n)"

            elif self.direction == "to":
                if self.start:
                    match_statement = "MATCH (:%s {uuid:'%s'})<-[r:%s]-" + "(n%s)" % start_labels

                else:
                    match_statement = "MATCH (:%s {uuid:'%s'})<-[r:%s]-(n)"

        elif direction == "bi":

            if self.direction == "from" or self.direction == "bi":
                if self.target:
                    match_statement = "MATCH (:%s {uuid:'%s'})-[r:%s]-" + "(n%s)" % target_labels

                else:
                    match_statement = "MATCH (:%s {uuid:'%s'})-[r:%s]-(n)"

            elif self.direction == "to":
                if self.start:
                    match_statement = "MATCH (:%s {uuid:'%s'})-[r:%s]-" + "(n%s)" % start_labels

                else:
                    match_statement = "MATCH (:%s {uuid:'%s'})-[r:%s]-(n)"

        else:
            bulb_logger.error(
                f'BULBRelationshipError("The \'direction\' argument of the get() method of a {self.__class__.__name__} instance, must be \'from\', \'to\', or \'bi\'.")')
            raise BULBRelationshipError(
                f"The 'direction' argument of the get() method of a {self.__class__.__name__} instance, must be 'from', 'to', or 'bi'.")

        # Build the where statement.
        if filter is not None:
            where_statement = "WHERE " + filter
            where_statement = where_statement.replace("n.", "r.")

        # Build other statements.
        return_statement_list = ["RETURN"]

        if isinstance(distinct, bool):
            if distinct is True:
                return_statement_list.append("DISTINCT")
        else:
            bulb_logger.error(
                f'BULBRelationshipError("The \'distinct\' argument of the get() method of a {self.__class__.__name__} instance, must be a boolean.")')
            raise BULBRelationshipError(
                f"The 'distinct' argument of the get() method of a {self.__class__.__name__} instance, must be a boolean.")

        if returned == "rel":
            with_statement = "WITH r"

            if order_by is not None:
                order_by_statement = "ORDER BY r.%s"

            if not only:
                return_statement_list.append("(r)")

            else:
                only_statement_list = []
                for element in only:
                    only_statement_list.append(f"r.{element}")

                only_statement = ", ".join(only_statement_list)

                return_statement_list.append(only_statement)

        elif returned == "node":
            with_statement = "WITH n"
            if order_by is not None:
                order_by_statement = "ORDER BY n.%s"

            if not only:
                return_statement_list.append("(n)")

            else:
                only_statement_list = []
                for element in only:
                    only_statement_list.append(f"n.{element}")

                only_statement = ", ".join(only_statement_list)

                return_statement_list.append(only_statement)

        elif returned == "both":
            with_statement = "WITH r, n"
            # return_statement_list.append("[r, n]")

            if order_by is not None:
                if order_by[:2] not in ["r.", "n."]:
                    bulb_logger.error(
                        f'BULBRelationshipError("The \'order_by\' argument of the get() method of a {self.__class__.__name__} instance, must start by \'r.\' or \'n.\' when the \'returned\' argument is \'both\'.")')
                    raise BULBRelationshipError(
                        f"The 'order_by' argument of the get() method of a {self.__class__.__name__} instance, must start by 'r.' or 'n.' when the 'returned' argument is 'both'.")

                order_by_statement = "ORDER BY %s"

            if not only:
                return_statement_list.append("[r, n]")

            else:
                only_statement = ", ".join(only)

                return_statement_list.append(only_statement)

        else:
            bulb_logger.error(
                f'BULBRelationshipError("The \'returned\' argument of the get() method of a {self.__class__.__name__} instance, must be \'rel\', \'node\' or \'both\'.")')
            raise BULBRelationshipError(
                f"The 'returned' argument of the get() method of a {self.__class__.__name__} instance, must be 'rel', 'node' or 'both'.")

        return_statement = " ".join(return_statement_list)

        # Add match_statement required variables.
        request_required_values_list.extend((self_node_instance.__class__.__name__,
                                             self_node_instance.uuid,
                                             self.rel_type))

        # Add order_by_statement required variable.
        if order_by is not None:
            request_required_values_list.append(order_by)

        # Build limit_statement and add its required variable.
        if limit is not None:
            limit_statement = "LIMIT %s"
            request_required_values_list.append(limit)

        # Build skip_statement and add its required variable.
        if skip is not None:
            skip_statement = "SKIP %s"
            request_required_values_list.append(skip)

        # Build desc_statement.
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
            response = gdbh.r_transaction(request_statement % tuple(request_required_values_list))

            if response:
                if only is None:

                    node_models_list = []
                    fake_instance_list = []

                    for database_object in response:
                        rel_object = None
                        node_object = None

                        if returned == "rel":
                            rel_object = database_object["r"]

                        elif returned == "node":
                            node_object = database_object["n"]

                        elif returned == "both":
                            rel_object = database_object["[r, n]"][0]
                            node_object = database_object["[r, n]"][1]

                        def render_nodes_and_relationships(node_model=None):
                            if returned == "rel":
                                fake_instance_list.append(self.__class__.build_fake_instance(rel_object,
                                                                                             forced_fake_instance_class=RelationshipInstance,
                                                                                             additional_parameters={
                                                                                                 "related_relationship": self}))
                            elif returned == "node":
                                fake_instance_list.append(self.__class__.build_fake_instance(node_object,
                                                                                             forced_fake_instance_class=node_model))

                            elif returned == "both":
                                fake_instance_list.append({"rel": self.__class__.build_fake_instance(rel_object,
                                                                                                     forced_fake_instance_class=RelationshipInstance,
                                                                                                     additional_parameters={
                                                                                                         "related_relationship": self}),
                                                           "node": self.__class__.build_fake_instance(node_object,
                                                                                                      forced_fake_instance_class=node_model)})

                        if self.start == "self" and self.target == "self":
                            render_nodes_and_relationships(self._self_node_instance.__class__)

                        else:
                            if not node_models_list:
                                # Collect all the node models.
                                node_models_list = get_all_node_models()

                            related_node_model_class_was_found = False
                            render_is_done = False

                            for node_model in node_models_list:

                                if self.direction == "from" or self.direction == "bi":
                                    if self.target is not None:
                                        if compare_different_modules_classes(self.target, node_model):
                                            render_nodes_and_relationships(node_model)
                                            related_node_model_class_was_found = True
                                            render_is_done = True

                                elif self.direction == "to":
                                    if self.start is not None:
                                        if compare_different_modules_classes(self.start, node_model):
                                            render_nodes_and_relationships(node_model)
                                            related_node_model_class_was_found = True
                                            render_is_done = True

                            # Handle case where no "start" and/or "target" constraints are applied to the relationship.
                            if render_is_done is False:
                                if returned == "rel":
                                    render_nodes_and_relationships()
                                    related_node_model_class_was_found = True

                                elif returned == "node" or returned == "both":
                                    for node_model in node_models_list:
                                        if node_model.__name__ in node_object.labels:
                                            render_nodes_and_relationships(node_model)
                                            related_node_model_class_was_found = True

                            if related_node_model_class_was_found is False:
                                bulb_logger.error(
                                    f'BULBRelationshipError("The node retrieved with the get() method of a {self.__class__.__name__} instance, matches with no one node_model of the project.")')
                                raise BULBRelationshipError(
                                    f"The node retrieved with the get() method of a {self.__class__.__name__} instance, matches with no one node_model of the project.")

                    return fake_instance_list

                else:
                    return response
            else:
                return None

        else:
            return request_statement % tuple(request_required_values_list)

    def count(self, direction="bi", returned="node", order_by=None, limit=None, skip=None, desc=False,
              distinct=False, only=None, filter=None, **extrafields):

        request_statement = self.get(direction=direction, returned=returned, order_by=order_by, limit=limit, skip=skip,
                                    desc=desc, distinct=distinct, only=only, filter=filter, return_query=True,
                                    **extrafields)

        returned_object = None

        if returned == "rel":
            returned_object = ["r"]

        elif returned == "node":
            returned_object = ["n"]

        elif returned == "both":
            returned_object = ["[r, n]"]

        request_count_statement = request_statement.split("RETURN")[0] + f"RETURN COUNT({returned_object})"
        response = gdbh.r_transaction(request_count_statement)

        return response[0][f"COUNT({returned_object})"]

    def remove(self, instance=None, uuid=None):
        if self.manage_is_done is False:
            self._manage_relationship_parameters()
            self.manage_is_done = True

        if instance is not None:
            gdbh.w_transaction("""
            MATCH (:%s {uuid:'%s'})-[r:%s {uuid:'%s'}]-({uuid:'%s'})
            DETACH DELETE (r)
            """ % (
                self._self_node_instance.__class__.__name__, self._self_node_instance.uuid, self.rel_type, self.uuid, instance.uuid))

        elif uuid is not None:
            response = gdbh.w_transaction("""
            MATCH (:%s {uuid:'%s'})-[r:%s]-({uuid:'%s'})
            DETACH DELETE (r)
            """ % (
                self._self_node_instance.__class__.__name__, self._self_node_instance.uuid, self.rel_type, uuid))

        else:
            bulb_logger.error(
                f'BULBRelationshipError("The remove() method of {self.__class__.__name__} instances must have as parameter either a node_model instance, or an \'uuid\'.")')
            raise BULBRelationshipError(
                f"The remove() method of {self.__class__.__name__} instances must have as parameter either a node_model instance, or an 'uuid'.")


class RelationshipInstance:
    """
    This class represents the relationships instance.
    """

    def __str__(self):
        return f'<{self.__class__.__name__} object(uuid="{self.uuid}")>'

    def __repr__(self):
        return f'<{self.__class__.__name__} object(uuid="{self.uuid}")>'

    def update(self, property_name, new_property_value):
        class_name = self.__class__.__name__
        properties_fields = self.related_relationship.__dict__["properties_fields"]

        if not settings.BULB_CREATE_PROPERTY_IF_NOT_FOUND and property_name not in properties_fields.keys():
            bulb_logger.warning(
                f'BULBRelationshipInstanceWarning("You are trying to update the property \'{property_name}\' of an {class_name} instance, but this property was not found in the instance dict. The update will have maybe no effect.")')
            warnings.warn(
                f"You are trying to update the property '{property_name}' of an {class_name} instance, but this property was not found in the instance dict. The update will have maybe no effect.",
                BULBRelationshipInstanceWarning)

        else:

            cypher_relation_type = ":" + self.rel_type
            cypher_properties_dict = "{uuid: '%s'}" % self.uuid

            # Create property if it not exists.
            if property_name not in self.__dict__.keys():
                try:
                    gdbh.w_transaction("""
                    MATCH ()-[r%s %s]->()
                    CALL apoc.create.setRelProperty(r, "%s", "%s") YIELD rel
                    RETURN (r)
                    """ % (cypher_relation_type, cypher_properties_dict,
                           property_name, None))

                except:
                    bulb_logger.warning(
                        f'BULBNodeWarning("You have defined BULB_CREATE_PROPERTY_IF_NOT_FOUND = True, but the neo4j\'s \'apoc\' plugin is not installed. So no new property was created.")')
                    warnings.warn(
                        f"You have defined BULB_CREATE_PROPERTY_IF_NOT_FOUND = True, but the neo4j's 'apoc' plugin is not installed. So no new property was created.",
                        BULBNodeWarning)

            # File handling (with SFTP storage)
            if properties_fields[property_name].sftp:

                if not isinstance(new_property_value, InMemoryUploadedFile) and not isinstance(new_property_value,
                                                                                               TemporaryUploadedFile):

                    if new_property_value == "None":

                        gdbh.w_transaction("""
                        MATCH ()-[r%s %s]->()
                        WHERE exists(r.%s)
                        SET r.%s = '%s'
                        """ % (cypher_relation_type, cypher_properties_dict,
                               property_name,
                               property_name, None))

                    else:
                        bulb_logger.error(
                            f'BULBPropertyError("The property \'{property_name}\' is configured with \'sftp=True\' but its value is neither a file nor \'None\'.")')
                        raise BULBPropertyError(
                            f"The property '{property_name}' is configured with 'sftp=True' but its value is neither a file nor 'None'.")

                else:

                    temporary_local_file_path, remote_file_path = compress_file_and_build_paths(new_property_value)

                    old_remote_file_path_for_purge = None

                    if properties_fields[property_name] != "None" and properties_fields[property_name] != "":
                        old_remote_file_path_for_purge = "/".join(properties_fields[property_name].split("/")[3:])

                    old_remote_file_path_for_remove = ("/www/" + old_remote_file_path_for_purge) if old_remote_file_path_for_purge is not None else None

                    with SFTP.connect() as sftp:
                        try:
                            sftp.put(temporary_local_file_path, remote_file_path)

                            try:
                                sftp.remove(old_remote_file_path_for_remove)

                            except:
                                pass

                            if old_remote_file_path_for_purge is not None:
                                if settings.BULB_USE_CDN77:
                                    from bulb.sftp_and_cdn.cdn_apis import CDN77

                                    try:
                                        CDN77.purge([old_remote_file_path_for_purge, ])

                                    except:
                                        pass

                        # Check and create default storage folders if they are not already created.
                        except IOError:
                            if not sftp.exists("/www/staticfiles"):
                                sftp.mkdir("/www/staticfiles")

                            if not sftp.exists("/www/staticfiles/content"):
                                sftp.mkdir("/www/staticfiles/content")

                            if not sftp.exists("/www/staticfiles/content/img"):
                                sftp.mkdir("/www/staticfiles/content/img")

                            if not sftp.exists("/www/staticfiles/content/pdf"):
                                sftp.mkdir("/www/staticfiles/content/pdf")

                            if not sftp.exists("/www/staticfiles/content/css"):
                                sftp.mkdir("/www/staticfiles/content/css")

                            if not sftp.exists("/www/staticfiles/content/js"):
                                sftp.mkdir("/www/staticfiles/content/js")

                            sftp.put(temporary_local_file_path, remote_file_path)

                            try:
                                sftp.remove(old_remote_file_path_for_remove)

                            except:
                                pass

                            if old_remote_file_path_for_purge is not None:
                                if settings.BULB_USE_CDN77:
                                    from bulb.sftp_and_cdn.cdn_apis import CDN77

                                    try:
                                        CDN77.purge([old_remote_file_path_for_purge, ])

                                    except:
                                        pass

                    os.remove(temporary_local_file_path)

                    full_stored_file_path_list = (settings.BULB_SFTP_PULL_URL + remote_file_path).split("/")
                    full_stored_file_path_list.pop(3)
                    full_stored_file_path = "/".join(full_stored_file_path_list)

                    gdbh.w_transaction("""
                    MATCH ()-[r%s %s]->()
                    WHERE exists(r.%s)
                    SET r.%s = '%s'
                    """ % (cypher_relation_type, cypher_properties_dict,
                           property_name,
                           property_name, full_stored_file_path))
                    new_property_value = full_stored_file_path

            # Integer, float, boolean and list handling.
            elif isinstance(new_property_value, int) or isinstance(new_property_value, float) or isinstance(new_property_value, bool) or isinstance(new_property_value, list):
                gdbh.w_transaction("""
                MATCH ()-[r%s %s]->()
                WHERE exists(r.%s)
                SET r.%s = %s
                """ % (cypher_relation_type, cypher_properties_dict,
                       property_name,
                       property_name, new_property_value))

            # Datetime handling
            elif isinstance(new_property_value, datetime.datetime):
                gdbh.w_transaction("""
                MATCH ()-[r%s %s]->()
                WHERE exists(r.%s)
                SET r.%s = datetime("%s")
                """ % (cypher_relation_type, cypher_properties_dict,
                       property_name,
                       property_name, str(new_property_value).replace(" ", "T")))

            # Date handling
            elif isinstance(new_property_value, datetime.date):
                gdbh.w_transaction("""
                MATCH ()-[r%s %s]->()
                WHERE exists(r.%s)
                SET r.%s = date("%s")
                """ % (cypher_relation_type, cypher_properties_dict,
                       property_name,
                       property_name, str(new_property_value)))

            # Time handling.
            elif isinstance(new_property_value, datetime.time):
                gdbh.w_transaction("""
                MATCH ()-[r%s %s]->()
                WHERE exists(r.%s)
                SET r.%s = time("%s")
                """ % (cypher_relation_type, cypher_properties_dict,
                       property_name,
                       property_name, str(new_property_value)))

            # String handling
            elif isinstance(new_property_value, str):
                # Escape quotes to prevent cypher syntax errors.
                new_property_value = new_property_value.replace('"', '\\"').replace("'", "\\'")

                gdbh.w_transaction("""
                MATCH ()-[r%s %s]->()
                WHERE exists(r.%s)
                SET r.%s = "%s"
                """ % (cypher_relation_type, cypher_properties_dict,
                       property_name,
                       property_name, new_property_value))

            # Other
            else:
                gdbh.w_transaction("""
                MATCH ()-[r%s %s]->()
                WHERE exists(r.%s)
                SET r.%s = '%s'
                """ % (cypher_relation_type, cypher_properties_dict,
                       property_name,
                       property_name, new_property_value))

            setattr(self, property_name, new_property_value)

    def delete(self):
        cypher_relation_type = ":" + self.rel_type
        cypher_properties_dict = "{uuid: '%s'}" % self.uuid

        gdbh.w_transaction("""
        MATCH ()-[r%s %s]->()
        DETACH DELETE (r)
        """ % (cypher_relation_type, cypher_properties_dict))
