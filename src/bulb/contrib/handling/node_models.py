from bulb.db import node_models, gdbh


class FakeClass:
    pass


class WebsiteSettings(node_models.Node):

    maintenance = node_models.Property(required=True)

    logo = node_models.Property(sftp=True)

    name = node_models.Property()

    def __str__(self):
        return f'<WebsiteSettings object>'

    def __repr__(self):
        return f'<WebsiteSettings object>'

    @classmethod
    def get(cls, uuid=None):
        response = gdbh.r_transaction('MATCH (w:WebsiteSettings) RETURN (w)')

        if response:
            fake_permission_instance = FakeClass()
            fake_permission_instance.__class__ = cls

            property_dict = response[0]["w"]._properties

            for property_name, property_value in property_dict.items():
                setattr(fake_permission_instance, property_name, property_value)

            return fake_permission_instance

        else:
            return None

    def delete(self):
        gdbh.w_transaction("""
        MATCH (w:WebsiteSettings)
        DETACH DELETE (w)
        """)
