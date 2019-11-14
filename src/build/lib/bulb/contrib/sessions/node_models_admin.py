Session_preview_fields = {"1": "uuid",
                          "2": "session_key",
                          "3": "expire_date"}

Session_fields_infos = {"uuid": {"type": "locked",
                                 "label": "UUID",
                                 "description": "C'est un identifiant unique et universel permettant une différenciation stricte entre chacun des noeuds."},

                        "session_key": {"type": "locked",
                                        "label": "Clé de session",
                                        "description": "Un clé de session est générée automatiquement pour chaque utilisateur qui se connecte. Elle permet d'identifier sa session et de garantir l'identité de l'utilisateur."},

                        "session_data": {"type": "locked",
                                         "label": "Données de session",
                                         "description": "Ces données chiffrées en base64 stockent l'UUID de l'utilisateur relié à cette session."},

                        "expire_date": {"type": "datetime",
                                        "label": "Date et heure d'expiration",
                                        "description": "Ces données chiffrées en base64 stockent l'UUID de l'utilisateur ainsi que la date et l'heure d'expiration de la session."},

                        "related_user": {"type": "relationship",
                                         "label": "Utilisateur",
                                         "rel": {
                                            "unique": True,
                                            "related_node_model_name": "User",
                                            "choices_render": ["first_name", "last_name"],
                                         }},
                        }