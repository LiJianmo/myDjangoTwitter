from accounts.models import UserProfile
from testing.testcase import TestCase


class UserProfileTests(TestCase):

    def test_profile_property(self):


        linghu, linghu_client = self.create_user_and_client('linghu')
        p = linghu.profile
        print(UserProfile.objects.count())
        # self.assertEqual(UserProfile.objects.count(), 0)
        # p = linghu.profile
        print(p)
        self.assertEqual(isinstance(p, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)
