from bulb.contrib.handling.exceptions import BULBAdminError
from bulb.contrib.auth.exceptions import BULBPermissionError
from bulb.contrib.auth.decorators import login_required, staff_only
from bulb.utils import get_files_paths_list, get_all_node_models
from bulb.contrib.auth.node_models import User
from bulb.utils.log import bulb_logger
from bulb.db import gdbh
from django.contrib.messages import add_message, SUCCESS, ERROR
from django.shortcuts import render, redirect
from django.http import JsonResponse, StreamingHttpResponse
from collections import OrderedDict
from django.conf import settings
from multiprocessing.dummy import Pool
import importlib.util
import datetime
import json
import time
import sys
import asyncio


login_page_url = "/" + settings.BULB_ADMIN_BASEPATH_NAME + "/login"


def get_admin_preview_fields(node_model_name):
    """
    This function return the _preview_fields dictionary of an instance if there is one, else it return None.
    First it tries to find the related dictionary into the project. If it isn't found, it tries to find the dictionary into
    bulb natives files.

    :param node_model_name:
    :return:
    """
    found_preview_fields_list = []

    # Try to find the related admin_preview_fields dict into the project folders and into bulb.
    node_models_admin_files_paths = get_files_paths_list('node_models_admin.py')

    for path in node_models_admin_files_paths:
        spec = importlib.util.spec_from_file_location("node_models_admin", path)
        node_models_admin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(node_models_admin)

        node_model_admin_dict = node_models_admin.__dict__

        # Try to find the corresponding admin infos dictionary.
        try:
            preview_fields_name = node_model_name + "_preview_fields"
            preview_fields_dict = node_model_admin_dict[preview_fields_name]

        except KeyError:
            pass

        else:
            found_preview_fields_list.append((path, preview_fields_dict))

    # Allow overloaded native preview fields.
    if len(found_preview_fields_list) > 1:
        selected_preview_fields = None

        for path, found_preview_fields in found_preview_fields_list:
            if not "/bulb/" in path:
                selected_preview_fields = found_preview_fields

        return selected_preview_fields

    elif len(found_preview_fields_list) == 1:
        return found_preview_fields_list[0][1]

    return None


def get_admin_fields(node_model_name):
    """
    This function return the _fields_infos dictionary of an instance if there is one, else it return None.
    First it tries to find the related dictionary into the project. If it isn't found, it tries to find the dictionary into
    bulb natives files.

    :param node_model_name:
    :return:
    """
    found_admin_fields_list = []

    # Try to find the related admin_fields dict into the project folders and into bulb.
    node_models_admin_files_paths = get_files_paths_list('node_models_admin.py')

    for path in node_models_admin_files_paths:
        spec = importlib.util.spec_from_file_location("node_models_admin", path)
        node_models_admin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(node_models_admin)

        node_model_admin_dict = node_models_admin.__dict__

        # Try to find the corresponding admin infos dictionary.
        try:
            admin_fields_name = node_model_name + "_fields_infos"
            admin_fields_dict = node_model_admin_dict[admin_fields_name]

        except KeyError:
            pass

        else:
            found_admin_fields_list.append((path, admin_fields_dict))

    # Allow overloaded native preview fields.
    if len(found_admin_fields_list) > 1:
        selected_admin_fields = None

        for path, found_admin_fields in found_admin_fields_list:
            if not "/bulb/" in path:
                selected_admin_fields = found_admin_fields

        return selected_admin_fields

    elif len(found_admin_fields_list) == 1:
        return found_admin_fields_list[0][1]

    return None


@staff_only()
@login_required(login_page_url=login_page_url)
def handling_home_view(request):

    node_models_names = []
    all_node_models = get_all_node_models()

    # For each path of the node_models.py files :
    for node_models in all_node_models:
        node_models_names.append(node_models.__name__)

    return render(request, "handling/pages/handling_home.html", {"node_classes_names": node_models_names})


@staff_only()
@login_required(login_page_url=login_page_url)
def node_model_home_view(request, node_model_name):
    # Check 'view' permission.
    if request.user.has_perm("view_" + node_model_name.lower()) or request.user.has_perm("view"):

        all_node_models = get_all_node_models()
        node_model = None

        for nm in all_node_models:
            if nm.__name__ == node_model_name:
                node_model = nm
                break

        if node_model is not None:
            preview_fields_dict = get_admin_preview_fields(node_model_name)

            if preview_fields_dict:

                # Define the order_by value.
                order_by = None
                if "order_by" in preview_fields_dict.keys():
                    order_by = preview_fields_dict["order_by"]
                    del preview_fields_dict["order_by"]

                else:
                    order_by = preview_fields_dict["1"]

                # Define the desc value.
                desc = ""
                if "desc" in preview_fields_dict.keys():
                    if preview_fields_dict["desc"] is True:
                        desc = "DESC"
                    del preview_fields_dict["desc"]

                # Define return statement.
                return_statement = "RETURN DISTINCT n.uuid AS uuid,"

                for key, value in preview_fields_dict.items():
                    return_statement = return_statement + f" n.{value},"

                return_statement = return_statement[:-1]

                # Load more request.
                if request.is_ajax():
                    loaded_instances = request.POST.get("loaded_instances")

                    new_instances = gdbh.r_transaction(f"""
                                                   MATCH (n:{node_model_name})

                                                   WITH n
                                                   ORDER BY n.{order_by}
                                                   {desc}
                                                   SKIP {loaded_instances}
                                                   LIMIT 20
                                                   {return_statement}
                                                    """)
                    if new_instances:
                        # String serialize all the reiceived objects.
                        for instance in new_instances:
                            for property_key, property_value in instance.items():
                                instance[property_key] = str(property_value)

                    return JsonResponse(json.dumps(new_instances), safe=False)

                # Initial request (when the page is loading).
                else:
                    number_of_instances = 0

                    twenty_last_instances = gdbh.r_transaction(f"""
                                                   MATCH (n:{node_model_name})

                                                   WITH n
                                                   ORDER BY n.{order_by}
                                                   {desc}
                                                   LIMIT 20
                                                   {return_statement}
                                                    """)

                    if twenty_last_instances:
                        # String serialize all the reiceived objects.
                        for instance in twenty_last_instances:
                            for property_key, property_value in instance.items():
                                instance[property_key] = str(property_value)

                        # Find the number of instances.
                        number_of_instances = gdbh.r_transaction(f"""
                                                       MATCH (n:{node_model_name})
                                                       RETURN COUNT(DISTINCT n)
                                                       """)[0]["COUNT(DISTINCT n)"]



                    return render(request, "handling/pages/node_class_home.html", locals())

            else:
                twenty_last_instances = node_model.get()

                try:
                    first_instance_uuid = twenty_last_instances.uuid

                except AttributeError:
                    return redirect("node_creation", node_model_name=node_model_name)

                else:
                    return redirect("node_handling", node_model_name=node_model_name, node_uuid="None")

    else:
        return redirect(settings.BULB_HOME_PAGE_URL)


@staff_only()
@login_required(login_page_url=login_page_url)
def node_model_home_search_view(request, node_model_name):

    if request.is_ajax():

        # Check 'view' permission.
        if request.user.has_perm("view_" + node_model_name.lower()) or request.user.has_perm("view"):

                preview_fields_dict = get_admin_preview_fields(node_model_name)

                # First search.
                if request.POST.get('value') and not request.POST.get("loaded_instances"):
                    value_to_search = request.POST.get('value')

                    # Define the order_by value.
                    order_by = None
                    if "order_by" in preview_fields_dict.keys():
                        order_by = preview_fields_dict["order_by"]
                        del preview_fields_dict["order_by"]

                    else:
                        order_by = preview_fields_dict["1"]

                    # Define the desc value.
                    desc = ""
                    if "desc" in preview_fields_dict.keys():
                        if preview_fields_dict["desc"] is True:
                            desc = "DESC"
                        del preview_fields_dict["desc"]

                    # Define the where and return statements.
                    where_statement = "WHERE"
                    return_statement = "RETURN DISTINCT n.uuid AS uuid,"

                    for key, value in preview_fields_dict.items():
                        where_statement = where_statement + f" n.{value} =~ '(?i)(.*){value_to_search}(.*)' OR"
                        return_statement = return_statement + f" n.{value},"

                    where_statement = where_statement[:-3]
                    return_statement = return_statement[:-1]

                    response = gdbh.r_transaction(f"""
                                                   MATCH (n:{node_model_name})
                                                   {where_statement}

                                                   WITH n
                                                   ORDER BY n.{order_by}
                                                   {desc}
                                                   LIMIT 20
                                                   {return_statement}
                                                    """)

                    if response:
                        response.append({"count": gdbh.r_transaction(f"""
                                                       MATCH (n:{node_model_name})
                                                       {where_statement}

                                                       RETURN COUNT(DISTINCT n)
                                                        """)[0]["COUNT(DISTINCT n)"]})

                        # String serialize all the reiceived objects.
                        for received_object in response:
                            for property_key, property_value in received_object.items():
                                received_object[property_key] = str(property_value)

                    return JsonResponse(response, safe=False)

                # More.
                if request.POST.get('value') and request.POST.get('loaded_instances'):

                    value_to_search = request.POST.get('value')
                    loaded_instances = request.POST.get("loaded_instances")

                    # Define the order_by value.
                    order_by = None
                    if "order_by" in preview_fields_dict.keys():
                        order_by = preview_fields_dict["order_by"]
                        del preview_fields_dict["order_by"]

                    else:
                        order_by = preview_fields_dict["1"]

                    # Define the desc value.
                    desc = ""
                    if "desc" in preview_fields_dict.keys():
                        if preview_fields_dict["desc"] == True:
                            desc = "DESC"
                        del preview_fields_dict["desc"]

                    # Define the where and return statements.
                    where_statement = "WHERE"
                    return_statement = "RETURN DISTINCT n.uuid AS uuid,"

                    for key, value in preview_fields_dict.items():
                        where_statement = where_statement + f" n.{value} =~ '(?i)(.*){value_to_search}(.*)' OR"
                        return_statement = return_statement + f"n.{value},"

                    where_statement = where_statement[:-3]
                    return_statement = return_statement[:-1]

                    new_instances = gdbh.r_transaction(f"""
                                                       MATCH (n:{node_model_name})
                                                       {where_statement}

                                                       WITH n
                                                       ORDER BY n.{order_by}
                                                       {desc}
                                                       SKIP {loaded_instances}
                                                       LIMIT 20
                                                       {return_statement}
                                                        """)

                    # String serialize all the reiceived objects.
                    for received_object in new_instances:
                        for property_key, property_value in received_object.items():
                            received_object[property_key] = str(property_value)

                    return JsonResponse(new_instances, safe=False)

        else:
            return redirect(settings.BULB_HOME_PAGE_URL)


def handle_edition(request, admin_fields_dict, node_model_name, instance, all_objects_dict):

    try:
        admin_request_post = dict(request.POST)
        admin_request_files = dict(request.FILES)
        admin_request = {**admin_request_post, **admin_request_files}

        if "action" in admin_request.keys():

            if admin_request["action"][0] == "update":

                # Remove the action of the request and the CSRF Token before uploading the new properties
                del admin_request["action"]
                del admin_request["csrfmiddlewaretoken"]

                # Store field's name and value if there is a password.
                password_field_name = None
                password_field_value = None
                password_confirmation_field_name = None
                password_confirmation_field_value = None

                for property_name, property_value in admin_request.items():

                    if property_value[0]:
                        # Ensure that it is not an helper field.
                        try:
                            related_admin_field_dict = admin_fields_dict[property_name]

                        except KeyError:
                            pass

                        else:
                            # Handle boolean values.
                            if property_value[0] == "on":
                                property_value[0] = True
                            elif property_value[0] == "off":
                                property_value[0] = False

                            # Handle datetime values.
                            elif related_admin_field_dict["type"] == "datetime":
                                if isinstance(property_value[0], str):
                                    try:
                                        # property_value[0] = datetime.datetime.fromisoformat(property_value[0]) # Doesn't work before Python 3.7
                                        property_value[0] = datetime.datetime(int(property_value[3]),
                                                                              int(property_value[2]),
                                                                              int(property_value[1]),
                                                                              int(property_value[4]),
                                                                              int(property_value[5]),
                                                                              int(property_value[6]))

                                    # Per default the Neo4j database add timezone (represented by 9 characters) to time object.
                                    except ValueError:
                                        # property_value[0] = datetime.datetime.fromisoformat(property_value[0][:-9]) # Doesn't work before Python 3.7
                                        property_value[0] = datetime.datetime(int(property_value[3]),
                                                                              int(property_value[2]),
                                                                              int(property_value[1]),
                                                                              int(property_value[4]),
                                                                              int(property_value[5]),
                                                                              int(property_value[6]))

                            # Handle date values.
                            elif related_admin_field_dict["type"] == "date":
                                if isinstance(property_value[0], str):
                                    try:
                                        # property_value[0] = datetime.date.fromisoformat(property_value[0]) # Doesn't work before Python 3.7
                                        property_value[0] = datetime.date(int(property_value[3]),
                                                                          int(property_value[2]),
                                                                          int(property_value[1]))

                                    # Per default the Neo4j database add timezone (represented by 9 characters) to time object.
                                    except ValueError:
                                        # property_value[0] = datetime.date.fromisoformat(property_value[0][:-9]) # Doesn't work before Python 3.7
                                        property_value[0] = datetime.date(int(property_value[3]),
                                                                          int(property_value[2]),
                                                                          int(property_value[1]))


                            # Handle time values.
                            elif related_admin_field_dict["type"] == "time":
                                if isinstance(property_value[0], str):
                                    try:
                                        str_to_datetime = datetime.datetime.strptime(property_value[0], "%H:%M:%S")
                                        datetime_to_time = datetime.datetime.time(str_to_datetime)
                                        property_value[0] = datetime_to_time

                                    # Per default the Neo4j database add milisecond (represented by 10 characters) to time object.
                                    except ValueError:
                                        str_to_datetime = datetime.datetime.strptime(property_value[0][:-10], "%H:%M:%S")
                                        datetime_to_time = datetime.datetime.time(str_to_datetime)
                                        property_value[0] = datetime_to_time

                        # Helpers fields and password.

                        # Handle passwords.
                        if property_name == "password-info":
                            password_field_name = property_value[0]
                            password_confirmation_field_name = f"{property_value[0]}-confirmation"

                        elif property_name == password_field_name:
                            password_field_value = property_value

                        elif property_name == password_confirmation_field_name:
                            password_confirmation_field_value = property_value

                            if password_field_value == password_confirmation_field_value:
                                instance.set_password(password_field_value[0])

                            else:
                                # TODO : Ajouter l'erreur sur le formulaire
                                # add_message(
                                #     request, ERROR,
                                #     "Le mot de passe et sa confirmation ne correspondent pas. Le mot de passe n'a donc pas été modifié.")
                                bulb_logger.error(
                                    'BULBAdminError("The password and its confirmation don\'t match. So the password was not modified.")')
                                raise BULBAdminError(
                                    "The password and its confirmation don\'t match. So the password was not modified.")

                        # Handle relationships.
                        elif property_name == "relationships-helper":
                            recovered_dict = json.loads(property_value[0])

                            for field_name, field_instructions in recovered_dict.items():
                                related_relationship_object = eval(f"instance.{field_name}")

                                add_list = field_instructions["add"]
                                remove_list = field_instructions["remove"]

                                if add_list:
                                    for to_add_uuid in add_list:

                                        # Check uuid to prevent HTML modification attack.
                                        uuid_is_valid = False
                                        for other_values_tuple in all_objects_dict[field_name]:
                                            if other_values_tuple[0] == to_add_uuid:
                                                uuid_is_valid = True
                                                break

                                        if uuid_is_valid is False:
                                            bulb_logger.error(
                                                'BULBAdminError("HTML modifications was found, the modifications cannot be done.")')
                                            raise BULBAdminError("HTML modifications was found, the modifications cannot be done.")

                                        related_relationship_object.add(uuid=to_add_uuid)

                                if remove_list:
                                    for to_remove_uuid in remove_list:

                                        # Check uuid to prevent HTML modification attack.
                                        uuid_is_valid = False
                                        for other_values_tuple in all_objects_dict[field_name]:
                                            if other_values_tuple[0] == to_remove_uuid:
                                                uuid_is_valid = True
                                                break

                                        if uuid_is_valid is False:
                                            bulb_logger.error(
                                                'BULBAdminError("HTML modifications was found, the modifications cannot be done.")')
                                            raise BULBAdminError("HTML modifications was found, the modifications cannot be done.")

                                        related_relationship_object.remove(uuid=to_remove_uuid)

                        # Handle unique relationships.
                        elif property_name == "unique-relationship-helper":
                            field_name = property_value[0].split(",")[0]
                            object_uuid = property_value[0].split(",")[1]

                            related_relationship_object = eval(f"instance.{field_name}")

                            # Check uuid to prevent HTML modification attack.
                            uuid_is_valid = False
                            for other_values_tuple in all_objects_dict[field_name]:
                                if other_values_tuple[0] == object_uuid:
                                    uuid_is_valid = True
                                    break

                            if uuid_is_valid is False:
                                bulb_logger.error(
                                    'BULBAdminError("HTML modifications was found, the modifications cannot be done.")')
                                raise BULBAdminError("HTML modifications was found, the modifications cannot be done.")

                            related_relationship_object.remove(uuid=object_uuid)

                        else:
                            instance.update(property_name, property_value[0])

                # add_message(request, SUCCESS, "L'instance a bien été mise à jour.")

                # if node_model_name:
                #     return redirect("node_model_home", node_model_name=node_model_name, permanent=True)
                #
                # else:
                #     return redirect("handling_home", permanent=True)

            elif admin_request["action"][0] == "delete":
                # Check 'delete' permission.
                if request.user.has_perm("delete_" + node_model_name.lower()) or request.user.has_perm("delete"):

                    instance.delete()
                    bulb_logger.activity(
                        f"{request.user.first_name} {request.user.last_name} ({request.user.uuid[:6]}) | delete | {node_model_name} | {instance.uuid[:6]}")
                    # add_message(request, SUCCESS, "L'instance a bien été supprimée.")

                    # if node_model_name:
                    #     return redirect("node_model_home", node_model_name=node_model_name, permanent=True)
                    #
                    # else:
                    #     return redirect("handling_home", permanent=True)

                else:
                    # add_message(request, ERROR, "Vous n'avez pas la permission de supprimer cette instance.")
                    # return redirect("node_handling", node_model_name=node_model_name, node_uuid=node_uuid)

                    bulb_logger.error('BULBPermissionError("You\'re not allowed to delete this instance.")')
                    raise BULBPermissionError("You're not allowed to delete this instance.")

        else:
            bulb_logger.error('BULBAdminError("You must provide the \'action\' key in the POST request.")')
            raise BULBAdminError("You must provide the 'action' key in the POST request.")

    except:
        raise
        # return sys.exc_info()


@staff_only()
@login_required(login_page_url=login_page_url)
def node_handling_view(request, node_model_name, node_uuid):
    # Check 'update' permission.
    if request.user.has_perm("update_" + node_model_name.lower()) or request.user.has_perm("update"):

        # Try to get the corresponding node model
        all_node_models = get_all_node_models()
        node_model = None

        # For each path of the node_models.py files :
        for found_node_model in all_node_models:
            if found_node_model.__name__ == node_model_name:
                node_model = found_node_model

        instance = node_model.get(uuid=node_uuid)

        admin_fields_dict = get_admin_fields(node_model_name)

        # Handle relationships
        all_objects_dict = {}
        selected_objects_dict = {}
        available_objects_dict = {}

        for field_name, field_settings, in admin_fields_dict.items():
            if field_settings["type"] == "relationship":
                all_objects_dict[field_name] = []

                # Get and store all the required datas for the selected_objects_dict.
                selected_objects = None

                try:
                    choices_render = field_settings['rel']['choices_render']

                except KeyError:
                    pass

                else:
                    if User in node_model.__mro__:
                        if field_name == "permissions":
                            selected_objects = eval(f"instance.{field_name}").get(order_by=choices_render[0],
                                                                                  only=["uuid"] + choices_render,
                                                                                  only_user_perms=True)
                        else:
                            selected_objects = eval(f"instance.{field_name}").get(order_by=choices_render[0],
                                                                                  only=["uuid"] + choices_render)

                    else:
                        selected_objects = eval(f"instance.{field_name}").get(order_by=choices_render[0],
                                                                              only=["uuid"] + choices_render)

                    if selected_objects is not None:
                        selected_objects_dict[field_name] = []
                        for selected_object in selected_objects:
                            values_tuple = []
                            for name, value in selected_object.items():
                                values_tuple.append(value)

                            values_tuple = tuple(values_tuple)
                            selected_objects_dict[field_name].append(values_tuple)
                            # all_objects_dict[field_name].append(values_tuple)

                    # Get and store all the required datas for the available_objects_dict.
                    for nm in all_node_models:

                        try:
                            related_node_model_name = field_settings['rel']['related_node_model_name']

                        except KeyError:
                            pass

                        else:
                            if nm.__name__ == related_node_model_name:
                                all_objects_response = {}
                                all_objects_response[field_name] = nm.get(order_by=choices_render[0],
                                                                          only=["uuid"] + choices_render)

                                if all_objects_response[field_name] is not None:
                                    for object_dict in all_objects_response[field_name]:
                                        values_tuple = []
                                        for name, value in object_dict.items():
                                            values_tuple.append(value)
                                        values_tuple = tuple(values_tuple)
                                        all_objects_dict[field_name].append(values_tuple)

                                    available_objects_dict[field_name] = []

                                    for values_tuple in all_objects_dict[field_name]:

                                        if selected_objects is not None:
                                            if values_tuple not in selected_objects_dict[field_name]:
                                                available_objects_dict[field_name].append(values_tuple)
                                        else:
                                            available_objects_dict[field_name].append(values_tuple)

        if request.POST or request.FILES:
            # handle_edition(request, admin_fields_dict, node_model_name, instance, all_objects_dict)

            pool = Pool(processes=1)

            def my_generator():
                yield '<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">'

                yield """
                            <style>
                                body {
                                    margin: 0;
                                }

                                p {
                                    font-size: 40px;
                                    margin-top: 0;
                                }

                                i {
                                    padding: 50px;
                                    padding-bottom: 20px;
                                    font-size: 100px;
                                }

                                i.valid-icons {
                                    color: #60db94;
                                }

                                i.error-icons {
                                    color: #e78586;
                                }

                                #loader {
                                    margin-top: 38.5px;
                                    width: 112px;
                                    height: 112px;
                                    transform: scale(0.5);
                                }

                                #loader .box1,
                                #loader .box2,
                                #loader .box3 {
                                    border: 16px solid #2d3436;
                                    box-sizing: border-box;
                                    position: absolute;
                                    display: block;
                                }

                                #loader .box1 {
                                    width: 112px;
                                    height: 48px;
                                    margin-top: 64px;
                                    margin-left: 0px;
                                    animation: anime1 4s 0s forwards ease-in-out infinite;
                                }

                                #loader .box2 {
                                    width: 48px;
                                    height: 48px;
                                    margin-top: 0px;
                                    margin-left: 0px;
                                    animation: anime2 4s 0s forwards ease-in-out infinite;
                                }

                                #loader .box3 {
                                    width: 48px;
                                    height: 48px;
                                    margin-top: 0px;
                                    margin-left: 64px;
                                    animation: anime3 4s 0s forwards ease-in-out infinite;
                                }

                                @-moz-keyframes anime1 {
                                    0% {
                                        width: 112px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    12.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    25% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    37.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    50% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    62.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    75% {
                                        width: 48px;
                                        height: 112px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    87.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    100% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }
                                }

                                @-webkit-keyframes anime1 {
                                    0% {
                                        width: 112px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    12.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    25% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    37.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    50% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    62.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    75% {
                                        width: 48px;
                                        height: 112px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    87.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    100% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }
                                }

                                @-o-keyframes anime1 {
                                    0% {
                                        width: 112px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    12.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    25% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    37.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    50% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    62.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    75% {
                                        width: 48px;
                                        height: 112px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    87.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    100% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }
                                }

                                @keyframes anime1 {
                                    0% {
                                        width: 112px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    12.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    25% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    37.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    50% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    62.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }

                                    75% {
                                        width: 48px;
                                        height: 112px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    87.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    100% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }
                                }

                                @-moz-keyframes anime2 {
                                    0% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    12.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    25% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    37.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    50% {
                                        width: 112px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    62.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    75% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    87.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    100% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }
                                }

                                @-webkit-keyframes anime2 {
                                    0% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    12.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    25% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    37.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    50% {
                                        width: 112px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    62.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    75% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    87.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    100% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }
                                }

                                @-o-keyframes anime2 {
                                    0% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    12.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    25% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    37.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    50% {
                                        width: 112px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    62.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    75% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    87.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    100% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }
                                }

                                @keyframes anime2 {
                                    0% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    12.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    25% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    37.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    50% {
                                        width: 112px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 0px;
                                    }

                                    62.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    75% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    87.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    100% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }
                                }

                                @-moz-keyframes anime3 {
                                    0% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    12.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    25% {
                                        width: 48px;
                                        height: 112px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    37.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    50% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    62.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    75% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    87.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    100% {
                                        width: 112px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }
                                }

                                @-webkit-keyframes anime3 {
                                    0% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    12.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    25% {
                                        width: 48px;
                                        height: 112px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    37.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    50% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    62.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    75% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    87.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    100% {
                                        width: 112px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }
                                }

                                @-o-keyframes anime3 {
                                    0% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    12.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    25% {
                                        width: 48px;
                                        height: 112px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    37.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    50% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    62.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    75% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    87.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    100% {
                                        width: 112px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }
                                }

                                @keyframes anime3 {
                                    0% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    12.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    25% {
                                        width: 48px;
                                        height: 112px;
                                        margin-top: 0px;
                                        margin-left: 64px;
                                    }

                                    37.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    50% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    62.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    75% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    87.5% {
                                        width: 48px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 64px;
                                    }

                                    100% {
                                        width: 112px;
                                        height: 48px;
                                        margin-top: 64px;
                                        margin-left: 0px;
                                    }
                                }
                            </style>"""

                yield """
                    <center id="loader-box">
                        <div id="loader">
                            <div class="box1"></div>
                            <div class="box2"></div>
                            <div class="box3"></div>
                        </div>
                        Loading...
                    </center>
                """

                # time.sleep(2)

                response = pool.apply_async(handle_edition,
                                           (request, admin_fields_dict, node_model_name, instance, all_objects_dict))


                while True:

                    if response.ready():
                        yield "<script>document.getElementById('loader-box').style.display = 'none';</script>"

                        if response.successful():
                            if not response.get():
                                if not dict(request.POST)["action"][0] == "delete":
                                    bulb_logger.activity(
                                        f"{request.user.first_name} {request.user.last_name} ({request.user.uuid[:6]}) | edit | {node_model_name} | {instance.uuid[:6]}")
                                yield "<center><i style='font-size: 150px;' class='material-icons valid-icons'>check_circle</i><br/><br/><p>Successful</p></center>"
                                time.sleep(2)
                                break

                            else:
                                yield "<center><i style='font-size: 150px;' class='material-icons error-icons'>cancel</i><br/><br/><p>Failed</p></center>"
                                time.sleep(2)
                                break
                        else:
                            yield "<center><i style='font-size: 150px;' class='material-icons error-icons'>cancel</i><br/><br/><p>Failed</p></center>"
                            time.sleep(2)
                            break

                    time.sleep(3)
                    yield "<span style='color: transparent;'>.</span>"


                yield """
                    <script>
                        function redirect_to_home () {
                            window.location.href = window.location.origin + '/admin/handling/%s'
                        }

                        redirect_to_home()
                    </script>
                """ % node_model_name

            return StreamingHttpResponse(my_generator())

        return render(request, "handling/pages/node_handling.html", locals())

    else:
        return redirect("node_model_home", node_model_name=node_model_name)


def handle_creation(request, admin_fields_dict, node_model, node_model_name, available_objects_dict):
    try:
        admin_request_post = request.POST
        admin_request_files = request.FILES
        admin_request = {**admin_request_post, **admin_request_files}

        properties = {}
        relationships_dict = {}

        for key, value in admin_request.items():
            if not key == "relationships-helper":
                properties[key] = value[0]

            else:
                relationships_dict = json.loads(value[0])

        del properties["csrfmiddlewaretoken"]

        try:
            password_field_name = properties["password-info"]

        except KeyError:
            pass

        else:
            password_field_value = properties[password_field_name]
            password_confirmation_field_name = f'{properties["password-info"]}-confirmation'
            password_confirmation_field_value = properties[password_confirmation_field_name]

            del properties["password-info"]
            del properties[password_confirmation_field_name]

            if not password_field_value == password_confirmation_field_value:
                del properties[password_field_name]
                # add_message(request, ERROR,
                #             "Le mot de passe et sa confirmation ne correspondent pas. Le mot de passe n'a donc pas été défini.")
                bulb_logger.error('BULBAdminError("The password and its confirmation do no match. So the instance was not created.")')
                raise BULBAdminError("The password and its confirmation do no match. So the instance was not created.")

        for property_name, property_value in properties.items():
            try:
                related_admin_field_dict = admin_fields_dict[property_name]

            except KeyError:
                pass

            else:
                if property_value:
                    # Handle boolean values.
                    if property_value == "on":
                        properties[property_name] = True
                    if property_value == "off":
                        properties[property_name] = False

                    # Handle datetime values.
                    if related_admin_field_dict["type"] == "datetime":
                        date_part = property_value.split(" ")[0].split("-")
                        time_part = property_value.split(" ")[1].split(":")

                        if isinstance(property_value, str):
                            try:
                                # property_value = datetime.datetime.fromisoformat(property_value) # Doesn't work before Python 3.7
                                properties[property_name] = datetime.datetime(int(date_part[0]),
                                                                   int(date_part[1]),
                                                                   int(date_part[2]),
                                                                   int(time_part[0]),
                                                                   int(time_part[1]),
                                                                   int(time_part[2]))

                            # Per default the Neo4j database add timezone (represented by 9 characters) to time object.
                            except ValueError:
                                # property_value = datetime.datetime.fromisoformat(property_value[:-9]) # Doesn't work before Python 3.7
                                properties[property_name] = datetime.datetime(int(date_part[0]),
                                                                   int(date_part[1]),
                                                                   int(date_part[2]),
                                                                   int(time_part[0]),
                                                                   int(time_part[1]),
                                                                   int(time_part[2]))

                    # Handle date values.
                    elif related_admin_field_dict["type"] == "date":

                        if isinstance(property_value, str):
                            try:
                                # property_value = datetime.date.fromisoformat(property_value) # Doesn't work before Python 3.7
                                properties[property_name] = datetime.date(int(property_value.split("-")[0]),
                                                               int(property_value.split("-")[1]),
                                                               int(property_value.split("-")[2]))

                            # Per default the Neo4j database add timezone (represented by 9 characters) to time object.
                            except ValueError:
                                # property_value = datetime.date.fromisoformat(property_value[:-9]) # Doesn't work before Python 3.7
                                properties[property_name] = datetime.date(int(property_value.split("-")[0]),
                                                               int(property_value.split("-")[1]),
                                                               int(property_value.split("-")[2]))


                    # Handle time values.
                    elif related_admin_field_dict["type"] == "time":

                        if isinstance(property_value, str):
                            try:
                                str_to_datetime = datetime.datetime.strptime(property_value, "%H:%M:%S")
                                datetime_to_time = datetime.datetime.time(str_to_datetime)
                                properties[property_name] = datetime_to_time

                            # Per default the Neo4j database add milisecond (represented by 10 characters) to time object.
                            except ValueError:
                                str_to_datetime = datetime.datetime.strptime(property_value[:-10], "%H:%M:%S")
                                datetime_to_time = datetime.datetime.time(str_to_datetime)
                                properties[property_name] = datetime_to_time

        new_instance = node_model.create(**properties)

        bulb_logger.activity(
            f"{request.user.first_name} {request.user.last_name} ({request.user.uuid[:6]}) | create | {node_model_name} | {new_instance.uuid[:6]}")

        for rel_name, rel_instructions in relationships_dict.items():
            related_relationship_object = eval(f"new_instance.{rel_name}")

            add_list = rel_instructions["add"]

            if add_list:
                for to_add_uuid in add_list:

                    # Check uuid to prevent HTML modification attack.
                    uuid_is_valid = False
                    for other_values_tuple in available_objects_dict[rel_name]:
                        if other_values_tuple[0] == to_add_uuid:
                            uuid_is_valid = True
                            break

                    if uuid_is_valid is False:
                        bulb_logger.error('BULBAdminError("HTML modifications was found, the modifications cannot be done.")')
                        raise BULBAdminError("HTML modifications was found, the modifications cannot be done.")

                    related_relationship_object.add(uuid=to_add_uuid)

        # admin_preview_fields = get_admin_preview_fields(node_model_name)

        # if admin_preview_fields is not False:
        #     return "preview fields"
        #
        # else:
        #     return "no preview fields"

    except:
        raise
        # return sys.exc_info()



@staff_only()
@login_required(login_page_url=login_page_url)
def node_creation_view(request, node_model_name):
    # Check 'create' permission.
    if request.user.has_perm("create_" + node_model_name.lower()) or request.user.has_perm("create"):

        # Try to get the corresponding node model
        all_node_models = get_all_node_models()
        node_model = None

        # For each path of the node_models.py files :
        for found_node_model in all_node_models:
            if found_node_model.__name__ == node_model_name:
                node_model = found_node_model

        admin_fields_dict = get_admin_fields(node_model_name)

        # Get availables objects for relationships.
        available_objects_dict = {}

        if admin_fields_dict is not None:
            for field_name, field_settings in admin_fields_dict.items():
                if field_settings["type"] == "relationship":

                    available_objects_dict[field_name] = []

                    for nm in all_node_models:
                        try:
                            related_node_model_name = field_settings['rel']['related_node_model_name']

                        except KeyError:
                            pass

                        else:
                            if nm.__name__ == field_settings['rel']['related_node_model_name']:
                                available_objects_response = {}
                                available_objects_response[field_name] = nm.get(order_by=field_settings['rel']['choices_render'][0],
                                                                                only=["uuid"] + field_settings['rel']['choices_render'])

                                if available_objects_response[field_name] is not None:
                                    for object_dict in available_objects_response[field_name]:
                                        values_tuple = []
                                        for name, value in object_dict.items():
                                            values_tuple.append(value)
                                        values_tuple = tuple(values_tuple)
                                        available_objects_dict[field_name].append(values_tuple)

            if request.POST or request.FILES:
                # handle_creation(request, admin_fields_dict, node_model, node_model_name, available_objects_dict)

                pool = Pool(processes=1)

                def my_generator():
                    yield '<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">'

                    yield """
                    <style>
                        body {
                            margin: 0;
                        }

                        p {
                            font-size: 40px;
                            margin-top: 0;
                        }

                        i {
                            padding: 50px;
                            padding-bottom: 20px;
                            font-size: 100px;
                        }

                        i.valid-icons {
                            color: #60db94;
                        }

                        i.error-icons {
                            color: #e78586;
                        }

                        #loader {
                            margin-top: 38.5px;
                            width: 112px;
                            height: 112px;
                            transform: scale(0.5);
                        }

                        #loader .box1,
                        #loader .box2,
                        #loader .box3 {
                            border: 16px solid #2d3436;
                            box-sizing: border-box;
                            position: absolute;
                            display: block;
                        }

                        #loader .box1 {
                            width: 112px;
                            height: 48px;
                            margin-top: 64px;
                            margin-left: 0px;
                            animation: anime1 4s 0s forwards ease-in-out infinite;
                        }

                        #loader .box2 {
                            width: 48px;
                            height: 48px;
                            margin-top: 0px;
                            margin-left: 0px;
                            animation: anime2 4s 0s forwards ease-in-out infinite;
                        }

                        #loader .box3 {
                            width: 48px;
                            height: 48px;
                            margin-top: 0px;
                            margin-left: 64px;
                            animation: anime3 4s 0s forwards ease-in-out infinite;
                        }

                        @-moz-keyframes anime1 {
                            0% {
                                width: 112px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            12.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            25% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            37.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            50% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            62.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            75% {
                                width: 48px;
                                height: 112px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            87.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            100% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }
                        }

                        @-webkit-keyframes anime1 {
                            0% {
                                width: 112px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            12.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            25% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            37.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            50% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            62.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            75% {
                                width: 48px;
                                height: 112px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            87.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            100% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }
                        }

                        @-o-keyframes anime1 {
                            0% {
                                width: 112px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            12.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            25% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            37.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            50% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            62.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            75% {
                                width: 48px;
                                height: 112px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            87.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            100% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }
                        }

                        @keyframes anime1 {
                            0% {
                                width: 112px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            12.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            25% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            37.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            50% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            62.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }

                            75% {
                                width: 48px;
                                height: 112px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            87.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            100% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }
                        }

                        @-moz-keyframes anime2 {
                            0% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            12.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            25% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            37.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            50% {
                                width: 112px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            62.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            75% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            87.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            100% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }
                        }

                        @-webkit-keyframes anime2 {
                            0% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            12.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            25% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            37.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            50% {
                                width: 112px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            62.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            75% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            87.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            100% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }
                        }

                        @-o-keyframes anime2 {
                            0% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            12.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            25% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            37.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            50% {
                                width: 112px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            62.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            75% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            87.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            100% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }
                        }

                        @keyframes anime2 {
                            0% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            12.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            25% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            37.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            50% {
                                width: 112px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 0px;
                            }

                            62.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            75% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            87.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            100% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }
                        }

                        @-moz-keyframes anime3 {
                            0% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            12.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            25% {
                                width: 48px;
                                height: 112px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            37.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            50% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            62.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            75% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            87.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            100% {
                                width: 112px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }
                        }

                        @-webkit-keyframes anime3 {
                            0% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            12.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            25% {
                                width: 48px;
                                height: 112px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            37.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            50% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            62.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            75% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            87.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            100% {
                                width: 112px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }
                        }

                        @-o-keyframes anime3 {
                            0% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            12.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            25% {
                                width: 48px;
                                height: 112px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            37.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            50% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            62.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            75% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            87.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            100% {
                                width: 112px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }
                        }

                        @keyframes anime3 {
                            0% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            12.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            25% {
                                width: 48px;
                                height: 112px;
                                margin-top: 0px;
                                margin-left: 64px;
                            }

                            37.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            50% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            62.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            75% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            87.5% {
                                width: 48px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 64px;
                            }

                            100% {
                                width: 112px;
                                height: 48px;
                                margin-top: 64px;
                                margin-left: 0px;
                            }
                        }
                    </style>"""

                    yield """
                        <center id="loader-box">
                            <div id="loader">
                                <div class="box1"></div>
                                <div class="box2"></div>
                                <div class="box3"></div>
                            </div>
                            Loading...
                        </center>
                    """

                    response = pool.apply_async(handle_creation,
                                                (request, admin_fields_dict, node_model, node_model_name, available_objects_dict))

                    yield "<span style='color: transparent;'>.</span>"

                    while True:
                        if response.ready():
                            yield "<script>document.getElementById('loader-box').style.display = 'none';</script>"

                            if response.successful():
                                if not response.get():
                                    yield "<center><i style='font-size: 150px;' class='material-icons valid-icons'>check_circle</i><br/><br/><p>Successful</p></center>"
                                    time.sleep(2)
                                    break

                                else:
                                    yield "<center><i style='font-size: 150px;' class='material-icons error-icons'>cancel</i><br/><br/><p>Failed</p></center>"
                                    time.sleep(2)
                                    break
                            else:
                                yield "<center><i style='font-size: 150px;' class='material-icons error-icons'>cancel</i><br/><br/><p>Failed</p></center>"
                                time.sleep(2)
                                break

                        time.sleep(3)
                        yield "<span style='color: transparent;'>.</span>"

                    yield """
                        <script>
                            function redirect_to_home () {
                                window.location.href = window.location.origin + '/admin/handling/%s'
                            }

                            redirect_to_home()
                        </script>
                    """ % node_model_name

                return StreamingHttpResponse(my_generator())

        return render(request, "handling/pages/node_creation.html", locals())

    else:
        return redirect("node_model_home", node_model_name=node_model_name)
