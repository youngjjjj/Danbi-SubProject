import random
from test_plus import APITestCase

from board.models import Boards


class BoardAPITestCase(APITestCase):

    def setUp(self):
        self.user1 = self.make_user(username='user1', password='strong_password_1')
        self.user2 = self.make_user(username='user2', password='strong_password_2')

    def create_board(self):
        self.post('/board/', data={
            'title': 'test'
        })

    def test_board_model(self):
        board = Boards.objects.create(author=self.user1, title="test")
        self.assertEqual(str(board), 'test')

    def test_board_get_anonymous_user(self):
        self.get('/board/')
        self.assert_http_403_forbidden()

    def test_board_get_authenticated_user(self):
        with self.login(username='user1', password='strong_password_1'):
            self.get('/board/')
            self.assert_http_200_ok()

    def test_board_post_anonymous_user(self):
        self.create_board()
        self.assert_http_403_forbidden()

    def test_board_post_authenticated_user(self):
        with self.login(username='user1', password='strong_password_1'):
            random_num = random.randint(3, 10)

            for _ in range(random_num):
                self.create_board()
                self.assert_http_201_created()

            boards = Boards.objects.all()
            board = Boards.objects.first()
            self.assertEqual(len(boards), random_num)
            self.assertEqual(board.author.username, 'user1')

    def test_board_put(self):
        with self.login(username='user1', password='strong_password_1'):
            self.create_board()

            # PUT method
            self.put('/board/1/', data={
                'title': 'fix'
            })
            self.assert_http_200_ok()
            board = Boards.objects.first()
            self.assertEqual(board.title, 'fix')

        with self.login(username='user2', password='strong_password_2'):
            self.create_board()
            self.put('/board/1/', data={
                'title': 'isNotAuthorFix'
            })
            self.assert_http_403_forbidden()
            board = Boards.objects.first()
            self.assertNotEqual(board.title, 'isNotAuthorFix')

    def test_board_patch(self):
        with self.login(username='user1', password='strong_password_1'):
            # PATCH method
            self.create_board()
            self.patch('/board/1/', data={
                'title': 'second fix'
            })
            self.assert_http_200_ok()
            second_board = Boards.objects.first()
            self.assertEqual(second_board.title, 'second fix')

        with self.login(username='user2', password='strong_password_2'):
            self.patch('/board/1/', data={
                'title': 'isNotAuthorFix'
            })
            self.assert_http_403_forbidden()
            board = Boards.objects.first()
            self.assertNotEqual(board.title, 'isNotAuthorFix')

    def test_board_delete(self):
        with self.login(username='user1', password='strong_password_1'):
            self.create_board()
            self.delete('/board/1/')
            self.assert_http_204_no_content()
            is_board = Boards.objects.exists()
            self.assertFalse(is_board)

        with self.login(username='user1', password='strong_password_1'):
            self.create_board()
            self.assert_http_201_created()

        with self.login(username='user2', password='strong_password_2'):
            self.delete('/board/2/')
            self.assert_http_403_forbidden()
            is_board = Boards.objects.exists()
            self.assertTrue(is_board)
