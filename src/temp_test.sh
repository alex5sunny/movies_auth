#!/bin/bash
source ../../venv/bin/activate
pytest tests/test_roles.py::test_create_role_success
pytest tests/test_roles.py::test_create_role_unauthorized
pytest tests/test_roles.py::test_get_roles
pytest tests/test_roles.py::test_get_role_by_id
pytest tests/test_roles.py::test_get_role_not_found
pytest tests/test_roles.py::test_update_role_success
pytest tests/test_roles.py::test_update_role_unauthorized
pytest tests/test_roles.py::test_delete_role_success
pytest tests/test_roles.py::test_delete_role_unauthorized

deactivate