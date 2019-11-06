from bulb.contrib.auth.node_models import make_uuid, get_user_node_model
from django.core.management import BaseCommand
from django.utils import timezone
from getpass import getpass

User = get_user_node_model()


class Command(BaseCommand):
    args = ""
    help = """
            Create a new super user.
           """

    def handle(self, *args, **options):
        datas_dict = {}

        print("Create a super user :")

        for field_name, field_content in User._get_properties_fields().items():
            property_name = field_content.key

            if property_name == 'is_super_user':
                datas_dict[property_name] = True

            elif property_name == 'is_staff_user':
                datas_dict[property_name] = True

            elif property_name == 'is_active_user':
                datas_dict[property_name] = True

            elif property_name == 'uuid':
                datas_dict[property_name] = make_uuid()

            elif property_name == 'password':
                pass

            elif property_name == 'registration_datetime':
                datas_dict[property_name] = timezone.now()

            else:
                property_value = input(f' - {property_name} : ')
                datas_dict[property_name] = property_value

        while True:
            password_property_value = getpass(' - password : ')
            password_confirmation_value = getpass(' - confirm password : ')

            if password_property_value == password_confirmation_value:
                datas_dict['password'] = password_property_value
                break

            else:
                print("(( Passwords do not match, please retry : ))")

        User.create_super_user(**datas_dict)
