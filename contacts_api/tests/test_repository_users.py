import unittest
from datetime import datetime, timedelta
from fastapi import HTTPException
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate
from app.repository.users import (
    create_user,
    authenticate_user,
    update_user_email_confirmation,
    update_user_avatar,
)


class TestUser(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = UserCreate(email="john.doe@example.com", username="John", password="Secret_password")

    @patch("app.repository.users.hash_password", return_value="hashed_pass")
    def test_create_user(self, mock_hash_password):
        mock_result = MagicMock()
        filter_mock = MagicMock()
        filter_mock.first.return_value = None
        mock_result.filter.return_value = filter_mock
        self.session.query.return_value = mock_result
        self.session.refresh = MagicMock()
        result = create_user(self.user, self.session)

        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(result)

        self.assertEqual(result.email, self.user.email)
        self.assertEqual(result.username, self.user.username)
        self.assertEqual(result.hashed_password, "hashed_pass")

    @patch("app.auth.security.verify_password", return_value=True)
    def test_authenticate_user(self, mock_verify_password):
        user = User(
            id=1,
            email=self.user.email,
            username=self.user.username,
            hashed_password="hashed_pass"
        )
        mock_result = self.session.query.return_value
        filter_mock = mock_result.filter.return_value
        filter_mock.first.return_value = user

        result = authenticate_user(self.user.email, self.user.password, self.session)
        self.assertEqual(result, user)
        mock_result = self.session.query.return_value
        filter_mock = mock_result.filter.return_value
        filter_mock.first.assert_called_once()

    @patch("app.auth.security.verify_password", return_value=False)
    def test_authenticate_user_invalid_password(self, mock_verify_password):
        user = User(
            id=1,
            email=self.user.email,
            username=self.user.username,
            hashed_password="hashed_pass"
        )
        mock_result = self.session.query.return_value
        filter_mock = mock_result.filter.return_value
        filter_mock.first.return_value = user
        result = authenticate_user(self.user.email, "wrong_password", self.session)
        self.assertIsNone(result)

    def test_update_user_email_confirmation_success(self):
        user = User(
            id=1,
            email=self.user.email,
            username=self.user.username,
            confirmed=False
        )
        mock_result = self.session.query.return_value
        filter_mock = mock_result.filter.return_value
        filter_mock.first.return_value = user
        self.session.refresh = MagicMock()

        result = update_user_email_confirmation(self.session, self.user.email)

        self.assertTrue(result.confirmed)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(user)
        self.assertEqual(result, user)

    def test_update_user_email_confirmation_user_not_found(self):
        mock_result = self.session.query.return_value
        filter_mock = mock_result.filter.return_value
        filter_mock.first.return_value = None

        result = update_user_email_confirmation(self.session, "not_found@email.com")

        self.assertIsNone(result)
        self.session.commit.assert_not_called()
        self.session.refresh.assert_not_called()

    def test_update_user_avatar_success(self):
        user = User(
            id=1,
            email=self.user.email,
            username=self.user.username,
            avatar_url=None,
        )
        self.new_avatar_url ="http://example.com/my_avatar.jpg"
        mock_result = self.session.query.return_value
        mock_filter = mock_result.filter.return_value
        mock_filter.first.return_value = user

        result = update_user_avatar(self.session, user, self.new_avatar_url)

        self.assertEqual(result.avatar, self.new_avatar_url)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(user)

    def test_update_user_avatar_user_not_found(self):
        user = User(
            id=1,
            email=self.user.email,
            username=self.user.username,
            avatar_url=None,
        )
        self.new_avatar_url = "http://example.com/my_avatar.jpg"
        mock_query = self.session.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_filter.first.return_value = None

        with self.assertRaises(HTTPException) as ex:
            update_user_avatar(self.session, user, self.new_avatar_url)

        self.assertEqual(ex.exception.status_code, 404)
        self.assertEqual(ex.exception.detail, "User not found")

        self.session.commit.assert_not_called()
        self.session.refresh.assert_not_called()


if __name__ == '__main__':
    unittest.main()
