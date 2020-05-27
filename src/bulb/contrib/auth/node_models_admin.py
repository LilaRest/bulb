from django.conf import settings


User_preview_fields = {"1": "last_name",
                       "2": "first_name",
                       "3": "email",
                       "4": "is_super_user",
                       "5": "is_staff_user",
                       "6": "is_active_user",
                       "7": "is_subscribed_user",
                       "order_by": "last_name",
                       "desc": True}

User_fields_infos = {"is_super_user": {"type": "checkbox",
                                       "label": "Super administrateur",
                                       "description": "Un super administrateur n'est soumis à aucune restriction. Il possède toutes les permissions."},

                     "is_staff_user": {"type": "checkbox",
                                       "label": "Administrateur",
                                       "description": "Un administrateur peut accéder aux différentes pages de l'interface d'administration. Cependant, cela ne lui donne aucunement le droit de créer, modifier ou supprimer quoi que ce soit."},

                     "is_active_user": {"type": "checkbox",
                                        "label": "Actif",
                                        "description": "Un compte utilisateur actif peut permettre de s'authentifier sur le site. Un utilisateur inactif est par exemple un compte utilisateur banni, qui ne pourra donc plus se connecter au site."},

                     "uuid": {"type": "locked",
                              "label": "UUID",
                              "description": "C'est un identifiant unique et universel permettant une différenciation stricte entre chacun des noeuds."},

                     "first_name": {"type": "text",
                                    "label": "Prénom"},

                     "last_name": {"type": "text",
                                   "label": "NOM"},

                     "email": {"type": "text",
                               "label": "Adresse email"},

                     "password": {"type": "password",
                                  "label": "Mot de passe"},

                     "registration_datetime": {"type": "datetime",
                                               "label": "Date et heure d'inscription"},

                     "session": {"type": "relationship",
                                 "label": "Session",
                                 "rel": {
                                     "unique": True,
                                     "related_node_model_name": "Session",
                                     "choices_render": ["session_key"],
                                 }},

                     "permissions": {"type": "relationship",
                                     "label": "Permissions",
                                     "rel": {
                                         "related_node_model_name": "Permission",
                                         "choices_render": ["codename"],
                                     }},

                     "groups": {"type": "relationship",
                                "label": "Groupes",
                                "rel": {
                                    "related_node_model_name": "Group",
                                    "choices_render": ["name"],
                                }}
                     }

if settings.BULB_REGISTRATION_USE_EMAIL_CONFIRMATION:
    User_fields_infos["email_is_confirmed"] = {
                            "type": "checkbox",
                            "label": "Confirmed email",
                            "description": "Indicate if the user's email is confirmed."
                        }

Permission_preview_fields = {"1": "codename",
                             "2": "description",
                             "order_by": "codename",
                             "desc": True}

Permission_fields_infos = {"uuid": {"type": "locked",
                                    "label": "UUID",
                                    "description": "C'est un identifiant unique et universel permettant une différenciation stricte entre chacun des noeuds."},
                           "codename": {"type": "text",
                                        "label": "Nom de code"},

                           "description": {"type": "text",
                                           "label": "Description"},

                           }

Group_preview_fields = {"1": "name",
                        "order_by": "codename",
                        "desc": True}

Group_fields_infos = {"uuid": {"type": "locked",
                                    "label": "UUID",
                                    "description": "C'est un identifiant unique et universel permettant une différenciation stricte entre chacun des noeuds."},
                      "name": {"type": "text",
                               "label": "Nom"},

                      "users": {"type": "relationship",
                                "label": "Utilisateurs",
                                "rel": {
                                    "related_node_model_name": "User",
                                    "choices_render": ["first_name", "last_name"],
                                }},

                      "permissions": {"type": "relationship",
                                      "label": "Permissions",
                                      "rel": {
                                          "related_node_model_name": "Permission",
                                          "choices_render": ["codename"],
                                      }},
                     }
