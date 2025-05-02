import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.models import Contact, User
from app.schemas import ContactCreate
from app.repository.contacts import (
    create_contact,
    get_all_contacts,
    get_contact_by_id,
    update_contact,
    delete_contact,
    search_contacts,
    get_upcoming_birthdays,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    def test_create_contact(self):
        body = ContactCreate(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890",
            birth_date="1990-01-01"
        )
        result = create_contact(db=self.session, contact=body, current_user=self.user)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birth_date, body.birth_date)

    def test_get_all_contacts(self):
        contacts = [Contact(), Contact()]
        mock_result = MagicMock()
        mock_result.all.return_value = contacts
        self.session.query.return_value.filter.return_value = mock_result
        result = get_all_contacts(db=self.session, current_user=self.user)
        self.assertEqual(result, contacts)

    def test_get_contact_by_id(self):
        contact = Contact()
        mock_result = MagicMock(return_value=contact)
        self.session.query.return_value.filter.return_value.first = mock_result
        result = get_contact_by_id(contact_id=1, db=self.session, current_user=self.user)
        self.assertEqual(result, contact)

    def test_get_contact_not_found(self):
        mock_result = MagicMock(return_value=None)
        self.session.query.return_value.filter.return_value.first = mock_result
        result = get_contact_by_id(contact_id=1, db=self.session, current_user=self.user)
        self.assertIsNone(result)

    def test_update_contact_found(self):
        contact = Contact()
        body = ContactCreate(
            first_name="Yuliia",
            last_name="Mykolenko",
            email="yuliia@example.com",
            phone_number="0987654321",
            birth_date="1992-02-02"
        )
        mock_result = MagicMock()
        filter_mock = MagicMock()
        filter_mock.first.return_value = contact
        mock_result.filter.return_value = filter_mock
        self.session.query.return_value = mock_result
        result = update_contact(contact_id=1, contact=body, db=self.session, current_user=self.user)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birth_date, body.birth_date)

    def test_update_contact_not_found(self):
        mock_result = MagicMock()
        filter_mock = MagicMock()
        filter_mock.first.return_value = None
        mock_result.filter.return_value = filter_mock
        self.session.query.return_value = mock_result
        body = ContactCreate(
            first_name="Yuliia",
            last_name="Mykolenko",
            email="yuliia@example.com",
            phone_number="0987654321",
            birth_date="1992-02-02"
        )
        result = update_contact(contact_id=1, contact=body, db=self.session, current_user=self.user)
        self.assertIsNone(result)

    def test_delete_contact_found(self):
        contact = Contact()
        mock_result = MagicMock(return_value=contact)
        self.session.query.return_value.filter.return_value.first = mock_result
        result = delete_contact(contact_id=1, db=self.session, current_user=self.user)
        self.assertEqual(result, contact)

    def test_delete_contact_not_found(self):
        mock_result = MagicMock(return_value=None)
        self.session.query.return_value.filter.return_value.first = mock_result
        result = delete_contact(contact_id=1, db=self.session, current_user=self.user)
        self.assertIsNone(result)

    def test_search_contacts_by_first_name(self):
        contacts = [Contact(first_name="John"), Contact(first_name="Yuliia")]
        mock_result = MagicMock()
        mock_result.all.return_value = contacts
        mock_filter = MagicMock()
        mock_filter.filter.return_value = mock_result
        self.session.query.return_value.filter.return_value = mock_filter
        result = search_contacts(first_name="John", last_name=None, email=None, db=self.session, current_user=self.user)
        self.assertEqual(result, contacts)

    def test_search_contacts_by_last_name(self):
        contacts = [Contact(last_name="Doe"), Contact(last_name="Mykolenko")]
        mock_result = MagicMock()
        mock_result.all.return_value = contacts
        mock_filter = MagicMock()
        mock_filter.filter.return_value = mock_result
        self.session.query.return_value.filter.return_value = mock_filter
        result = search_contacts(first_name=None, last_name="Doe", email=None, db=self.session, current_user=self.user)
        self.assertEqual(result, contacts)

    def test_search_contacts_by_email(self):
        contacts = [Contact(email="example@email.com"), Contact(email="example1@email.com")]
        mock_result = MagicMock()
        mock_result.all.return_value = contacts
        mock_filter = MagicMock()
        mock_filter.filter.return_value = mock_result
        self.session.query.return_value.filter.return_value = mock_filter
        result = search_contacts(first_name=None, last_name=None, email="example", db=self.session,
                                 current_user=self.user)
        self.assertEqual(result, contacts)

    def test_get_upcoming_birthdays(self):
        today = datetime.today().date()
        contact_today = Contact(birth_date=today)
        contact_in_5_days = Contact(birth_date=today + timedelta(days=5))
        contact_in_8_days = Contact(birth_date=today + timedelta(days=8))

        mock_filter = MagicMock()
        mock_filter.all.return_value = [contact_today, contact_in_5_days, contact_in_8_days]
        self.session.query.return_value.filter.return_value = mock_filter
        result = get_upcoming_birthdays(db=self.session, current_user=self.user)

        self.assertIn(contact_today, result)
        self.assertIn(contact_in_5_days, result)
        self.assertNotIn(contact_in_8_days, result)


if __name__ == '__main__':
    unittest.main()
