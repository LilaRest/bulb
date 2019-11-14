import uuid


def make_uuid():
    return uuid.uuid4().hex


def compare_different_modules_classes(class1, class2):
    class2.__module__ = class1.__module__
    if class1.__name__ == class2.__name__ and class1.__dict__.keys() == class2.__dict__.keys():
        return True
    return False
