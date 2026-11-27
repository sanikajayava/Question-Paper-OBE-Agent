import unittest
from unittest.mock import patch

from auth_ui import bootstrap_admin_from_secrets


class CloudDeploymentTests(unittest.TestCase):
    def test_initial_admin_is_created_from_streamlit_secrets(self):
        secrets = {
            "initial_admin": {
                "id": "cloud-admin",
                "password": "strong-password",
            }
        }

        with patch("auth_ui.st.secrets", secrets), \
                patch("auth_ui.create_admin") as create_admin:
            bootstrap_admin_from_secrets()

        create_admin.assert_called_once_with("cloud-admin", "strong-password")


if __name__ == "__main__":
    unittest.main()
