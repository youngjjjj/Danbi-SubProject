import random
from test_plus import APITestCase

from board.models import Boards


class BoardAPITestCase(APITestCase):

    def setUp(self):
        self.user1 = self.make_user(username='user1', password='strong_password_1')
        self.user2 = self.make_user(username='user2', password='strong_password_2')


    def create_board_with_assert(self, status_code=201, num=1):
        for _ in range(num):
            response = self.post('/board/', data={
                'content': 'test'
            })

            self.assertEqual(status_code, response.status_code)


    def create_board(self):
        self.post('/board/', data={
            'content': 'test'
        })

    def test_board_get_anonymous_user(self):
        self.get('/board/')
        self.assert_http_403_forbidden()

    def test_board_get_authenticated_user(self):
        with self.login(username='user1', password='strong_password_1'):
            self.get('/board/')
            self.assert_http_200_ok()

    def test_board_post_anonymous_user(self):
        # self.create_board_with_assert(status_code=403)
        self.create_board()
        self.assert_http_403_forbidden()
        breakpoint()

    def test_board_post_authenticated_user(self):
        with self.login(username='user1', password='strong_password_1'):
            random_num = random.randint(3, 10)
            self.create_board_with_assert(status_code=201, num=random_num)


    def test_board_put(self):
        with self.login(username='user1', password='strong_password_1'):
            self.create_board_with_assert(status_code=201)

            # PUT method
            self.put('/board/1/', data={
                'content': 'fix'
            })
            self.assert_http_200_ok()
            board = Boards.objects.first()
            self.assertEqual(board.content, 'fix')

        with self.login(username='user2', password='strong_password_2'):
            self.put('/board/1/', data={
                'content': 'isNotAuthorFix'
            })
            self.assert_http_403_forbidden()
            board = Boards.objects.first()
            self.assertNotEqual(board.content, 'isNotAuthorFix')

    def test_board_patch(self):
        with self.login(username='user1', password='strong_password_1'):
            # PATCH method
            self.create_board_with_assert()
            self.patch('/board/1/', data={
                'content': 'second fix'
            })
            self.assert_http_200_ok()
            second_board = Boards.objects.first()
            self.assertEqual(second_board.content, 'second fix')

        with self.login(username='user2', password='strong_password_2'):
            self.put('/board/1/', data={
                'content': 'isNotAuthorFix'
            })
            self.assert_http_403_forbidden()
            board = Boards.objects.first()
            self.assertNotEqual(board.content, 'isNotAuthorFix')


    def test_board_delete(self):
        with self.login(username='user1', password='strong_password_1'):
            self.create_board_with_assert()
            self.delete('/board/1/')
            self.assert_http_204_no_content()
            is_board = Boards.objects.exists()
            self.assertFalse(is_board)

        self.create_board_with_assert(user='user2')
        self.client.logout()
        self.login_user_1()
        self.delete('/board/1/')
        self.assert_http_403_forbidden()
        is_board = Boards.objects.exists()
        self.assertTrue(is_board)

    def test_example(self):
        self.post('/board/', data={
            'content': 'test'
        })
        self.assert_http_403_forbidden()




