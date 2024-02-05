from django.test import TestCase, RequestFactory


# Create your tests here.
class APITEST(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_api(self):
        from .views import rest_signup, rest_login, rest_test_token

        user_data = {"username": "TestUser", "password": "Pass1234!"}

        signup_request = self.factory.post(path="/signup", data=user_data)
        login_request = self.factory.post(path="/login", data=user_data)

        signup_response = rest_signup(signup_request)
        login_response = rest_login(login_request)
        self.assertTrue(
            "username" in signup_response.data or "token" in signup_response.data
        )
        self.assertIn("token", login_response.data)
        test_token_request = self.factory.get(
            path="/test_token",
            headers={"Authorization": f"Token {login_response.data['token']}"},
        )
        test_token_response = rest_test_token(test_token_request)
        self.assertTrue("Success for user:" in test_token_response.data)
