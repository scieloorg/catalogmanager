import catalogmanager


# def test_get_article(couchdb_article_location,
#                      database_config,
#                      xml_test):
#     _, _, article_id = couchdb_article_location.split('/')
#     article_check = catalogmanager.get_article_data(article_id,
#                                                     *database_config)
#     assert article_check is not None
#     assert isinstance(article_check, dict)
#     assert article_check['document_id'] == article_id
#     assert article_check['created_date'] is not None
#     assert article_check['content'] is not None
#     assert isinstance(article_check['content'], dict)


def test_add_article_register_change(functional_config,
                                     change_service):
    # Setup database config

    # An item is registered in persistence module. E.g.: Article

    # A change register must be created. E.g.: Article insertion

    # First, check if list of changes bring the change register

    # Finally, get the register by identification

    # It must have an accessible URL to get the XML file
    pass
