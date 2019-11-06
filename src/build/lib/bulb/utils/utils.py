from django.conf import settings
import importlib.util
import os

BASE_DIR = settings.BASE_DIR


def get_folders_paths_list(folders_name):
    """
    This function returns the list of paths of all the folders named with the 'folders_name' value.
    """
    folders_paths = []

    # First, search into the project.
    for root, dirs, files in os.walk(BASE_DIR):
        if folders_name in dirs:
            folders_paths.append(os.path.join(root, folders_name))

    # Then, into the bulb source files.
    # for root, dirs, files in os.walk(bulb.__path__[0]):
    import bulb
    bulb_path = bulb.__path__[0]
    for root, dirs, files in os.walk(bulb_path):
        if folders_name in dirs:
            folders_paths.append(os.path.join(root, folders_name))

    if len(folders_paths) == 0:
        return None

    elif len(folders_paths) == 1:
        return folders_paths[0]

    return folders_paths


def get_files_paths_list(files_name, from_project=True, from_BULB=True):
    """
    This function returns the list of paths of all the folders named with the 'folders_name' value.
    """
    files_paths = []

    # First, search into the project.
    if from_project is True:
        for root, dirs, files in os.walk(BASE_DIR):
            if not root.startswith("/app/.heroku/python"): # Prevent Heroku bug (file organization is different and the bulb node_models are found two times)
                if files_name in files:
                    files_paths.append(os.path.join(root, files_name))

    # Then, into the bulb source files.
    if from_BULB is True:
        # for root, dirs, files in os.walk(bulb.__path__[0]):
        import bulb
        bulb_path = bulb.__path__[0]
        for root, dirs, files in os.walk(bulb_path):
            if files_name in files:
                # Exclude the db node_models.
                if not "bulb/db" in root:
                    files_paths.append(os.path.join(root, files_name))

    if len(files_paths) == 0:
        return None

    elif len(files_paths) == 1:
        return files_paths[0]

    return files_paths


def get_all_node_models():
    """
    This function returns the list of all the node_models of the project. It cares about inheritance and overloading.
    """
    from bulb.contrib.auth.node_models import get_user_node_model, get_permission_node_model, get_group_node_model
    from bulb.contrib.sessions.node_models import get_session_node_model
    from bulb.db.node_models import Node
    node_models_list = []

    # # Allow overloaded native classes.
    Permission_class_is_needed = False
    Group_class_is_needed = False
    User_class_is_needed = False
    Session_class_is_needed = False

    for file_path in get_files_paths_list("node_models.py"):

        # Import the module from his path
        spec = importlib.util.spec_from_file_location("node_models", file_path)
        node_models = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(node_models)

        # Get all the module classes that have in their parents the Node class.
        node_model_dict = node_models.__dict__

        for k, v in node_model_dict.items():
            try:
                # Explanation : __module__ return only the name of the module where is contained the node_class (here :
                # "node_models"), but if the node_class is an import, __module__ return the full module path (example :
                # "bulb.contrib.sessions.node_models"). So, this line prevent the detection of the imported
                # classes in the node_models files.
                if Node in v.__mro__ and v.__module__ == "node_models":

                    # # Add overloaded native classes.
                    if v.__name__ == "Permission":
                        Permission_class_is_needed = True

                    elif v.__name__ == "Group":
                        Group_class_is_needed = True

                    elif v.__name__ == "User":
                        User_class_is_needed = True

                    elif v.__name__ == "Session":
                        Session_class_is_needed = True

                    else:
                        node_models_list.append(v)

            except:
                pass

    # # Add overloaded native classes.
    if Permission_class_is_needed:
        node_models_list.append(get_permission_node_model())

    if Group_class_is_needed:
        node_models_list.append(get_group_node_model())

    if User_class_is_needed:
        node_models_list.append(get_user_node_model())

    if Session_class_is_needed:
        node_models_list.append(get_session_node_model())

    return node_models_list