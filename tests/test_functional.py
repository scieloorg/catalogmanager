

def test_functional_home(testapp):
    resp = testapp.get('/', status=200)
    assert resp.status == '200 OK'
    assert resp.status_code == 200


def test_add_article_register_change(functional_config,
                                     change_service):
    # An item is registered in persistence module. E.g.: Article
    # A change register must be created. E.g.: Article insertion
    # First, check if list of changes bring the change register
    # Finally, get the register by identification
    pass
