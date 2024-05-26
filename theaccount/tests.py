from django.test import TestCase
from django.conf import settings
from .models import User, UserProfile, Contact

class UserModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='safa@example.com',
            first_name='safa',
            last_name='abouzaid',
            password='testpass123',
            balance=1000.00,
            pointBalance=50,
            fcm_token='testfcm123'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'safa@example.com')
        self.assertEqual(self.user.first_name, 'safa')
        self.assertEqual(self.user.last_name, 'abouzaid')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertEqual(self.user.balance, 1000.00)
        self.assertEqual(self.user.pointBalance, 50)
        self.assertEqual(self.user.fcm_token, 'testfcm123')

class UserProfileModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='safa@example.com', password='testpass123')
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            gender='female',
            age=30,
            address='123 Main St',
            marital_status='single',
            occupation='engineer'
        )

    def test_user_profile_creation(self):
        self.assertEqual(self.user_profile.user.username, 'safa@example.com')
        self.assertEqual(self.user_profile.gender, 'female')
        self.assertEqual(self.user_profile.age, 30)
        self.assertEqual(self.user_profile.address, '123 Main St')
        self.assertEqual(self.user_profile.marital_status, 'single')
        self.assertEqual(self.user_profile.occupation, 'engineer')

class ContactModelTest(TestCase):
    
    def setUp(self):
        self.contact = Contact.objects.create(
            name='Jane Doe',
            email='jane.doe@example.com',
            message='Hello, this is a test message.'
        )

    def test_contact_creation(self):
        self.assertEqual(self.contact.name, 'Jane Doe')
        self.assertEqual(self.contact.email, 'jane.doe@example.com')
        self.assertEqual(self.contact.message, 'Hello, this is a test message.')
