from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .utils import make_tag, make_user, prepare_project


class TestTagList(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.project = prepare_project()
        cls.non_member = make_user(username='bob')
        make_tag(project=cls.project.item)
        cls.url = reverse(viewname='tag_list', args=[cls.project.item.id])

    def test_return_tags_to_member(self):
        for member in self.project.users:
            self.client.force_login(member)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)

    def test_does_not_return_tags_to_non_member(self):
        self.client.force_login(self.non_member)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_does_not_return_tags_to_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestTagCreate(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.project = prepare_project()
        cls.non_member = make_user(username='bob')
        cls.url = reverse(viewname='tag_list', args=[cls.project.item.id])
        cls.data = {'text': 'example'}

    def assert_create_tag(self, user=None, expected=status.HTTP_403_FORBIDDEN):
        if user:
            self.client.force_login(user)
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, expected)
        return response

    def test_allow_admin_to_create_tag(self):
        response = self.assert_create_tag(self.project.users[0], status.HTTP_201_CREATED)
        self.assertEqual(response.data['text'], self.data['text'])

    def test_disallow_non_admin_to_create_tag(self):
        for member in self.project.users[1:]:
            self.assert_create_tag(member, status.HTTP_403_FORBIDDEN)

    def test_disallow_unauthenticated_user_to_create_tag(self):
        self.assert_create_tag(expected=status.HTTP_403_FORBIDDEN)


class TestTagDelete(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.project = prepare_project()
        cls.non_member = make_user(username='bob')

    def setUp(self):
        tag = make_tag(project=self.project.item)
        self.url = reverse(viewname='tag_detail', args=[self.project.item.id, tag.id])

    def assert_delete_tag(self, user=None, expected=status.HTTP_403_FORBIDDEN):
        if user:
            self.client.force_login(user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, expected)

    def test_allow_admin_to_delete_tag(self):
        self.assert_delete_tag(self.project.users[0], status.HTTP_204_NO_CONTENT)

    def test_disallow_non_admin_to_delete_tag(self):
        for member in self.project.users[1:]:
            self.assert_delete_tag(member, status.HTTP_403_FORBIDDEN)

    def test_disallow_unauthenticated_user_to_delete_tag(self):
        self.assert_delete_tag(expected=status.HTTP_403_FORBIDDEN)
