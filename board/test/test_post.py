import random
from test_plus import APITestCase

from board.models import Post, Boards


class PostAPITestCase(APITestCase):

    def setUp(self):
        self.user1 = self.make_user(username='user1', password='strong_password_1')
        self.user2 = self.make_user(username='user2', password='strong_password_2')
        self.board_pk = 0
        self.post_pk = 0

    def create_board(self):
        self.post('/board/', data={
            'title': 'test',
        })
        self.board_pk += 1

    def create_post(self, board_pk):
        self.post(f'/board/{board_pk}/post/', data={
            'title': 'title',
            'content': 'content',
        })
        self.post_pk += 1

    def test_post_model(self):
        board = Boards.objects.create(author=self.user1, title='test')
        post = Post.objects.create(author=self.user1, board=board, title='title', content='content')
        self.assertEqual(str(post), 'title')

    def test_post_create_anonymous_user(self):
        self.create_board()
        self.create_post(self.board_pk)
        self.assert_http_403_forbidden()
        is_post = Post.objects.exists()
        self.assertFalse(is_post)

    def test_post_create_authenticated_user(self):
        with self.login(username='user1', password='strong_password_1'):
            random_num = random.randint(3, 10)

            self.create_board()

            for _ in range(random_num):
                self.create_post(self.board_pk)
                self.assert_http_201_created()

            posts = Post.objects.all()
            self.assertEqual(len(posts), random_num)

    def test_post_put(self):
        with self.login(username='user1', password='strong_password_1'):
            self.create_board()
            self.create_post(self.board_pk)

            # PUT method
            self.put(f'/board/{self.board_pk}/post/{self.post_pk}/', data={
                'title': 'fix_title',
                'content': 'fix_content',
            })
            self.assert_http_200_ok()
            post = Post.objects.first()
            self.assertEqual(post.title, 'fix_title')
            self.assertEqual(post.content, 'fix_content')

        # Anonymous user
        self.put(f'/board/{self.board_pk}/post/{self.post_pk}/', data={
            'title': 'isNotAuthorFix_title',
            'content': 'isNotAuthorFix_content',
        })
        self.assert_http_403_forbidden()

        # Is not post author user
        with self.login(username='user2', password='strong_password_2'):
            self.put(f'/board/{self.board_pk}/post/{self.post_pk}/', data={
                'title': 'isNotAuthorFix_title',
                'content': 'isNotAuthorFix_content',
            })
            self.assert_http_403_forbidden()
            post = Post.objects.first()
            self.assertNotEqual(post.title, 'isNotAuthorFix_title')
            self.assertNotEqual(post.content, 'isNotAuthorFix_content')

    def test_post_delete(self):
        with self.login(username='user1', password='strong_password_1'):
            self.create_board()
            self.create_post(self.board_pk)

            self.delete(f'/board/{self.board_pk}/post/{self.post_pk}/')
            self.assert_http_204_no_content()
            is_post = Post.objects.exists()
            self.assertFalse(is_post)

            self.create_post(self.board_pk)

        with self.login(username='user2', password='strong_password_2'):
            self.delete(f'/board/{self.board_pk}/post/{self.post_pk}/')
            self.assert_http_403_forbidden()
            is_post = Post.objects.exists()
            self.assertTrue(is_post)

        self.delete(f'/board/{self.board_pk}/post/{self.post_pk}/')
        self.assert_http_403_forbidden()
        is_post = Post.objects.exists()
        self.assertTrue(is_post)

    def test_post_like_create(self):
        with self.login(username='user1', password='strong_password_1'):
            self.create_board()
            self.create_post(self.board_pk)

        self.post(f'/board/{self.board_pk}/post/{self.post_pk}/like/')
        self.assert_http_403_forbidden()
        post = Post.objects.first()
        like_count = post.like_post.count()
        self.assertEqual(like_count, 0)

        with self.login(username='user2', password='strong_password_2'):
            self.post(f'/board/{self.board_pk}/post/{self.post_pk}/like/')
            self.assert_http_201_created()
            post = Post.objects.first()
            like_count = post.like_post.count()
            self.assertEqual(like_count, 1)

            self.post(f'/board/{self.board_pk}/post/{self.post_pk}/like/')
            self.assert_http_400_bad_request()
            post = Post.objects.first()
            like_count = post.like_post.count()
            self.assertEqual(like_count, 1)

    def test_post_like_get(self):
        with self.login(username='user1', password='strong_password_1'):
            self.create_board()
            self.create_post(self.board_pk)

        self.get(f'/board/{self.board_pk}/post/{self.post_pk}/like/')
        self.assert_http_403_forbidden()

        with self.login(username='user1', password='strong_password_1'):
            self.get(f'/board/{self.board_pk}/post/{self.post_pk}/like/')
            self.assert_http_400_bad_request()

            self.post(f'/board/{self.board_pk}/post/{self.post_pk}/like/')
            response = self.get(f'/board/{self.board_pk}/post/{self.post_pk}/like/')
            self.assert_http_200_ok()
            self.assertEqual(response.data[0]['username'], 'user1')

    def test_post_like_delete(self):
        with self.login(username='user1', password='strong_password_1'):
            self.create_board()
            self.create_post(self.board_pk)
            self.post(f'/board/{self.board_pk}/post/{self.post_pk}/like/')

        self.delete(f'/board/{self.board_pk}/post/{self.post_pk}/like/')
        self.assert_http_403_forbidden()

        with self.login(username='user2', password='strong_password_2'):
            self.delete(f'/board/{self.board_pk}/post/{self.post_pk}/like/')
            self.assert_http_400_bad_request()

        with self.login(username='user1', password='strong_password_1'):
            self.delete(f'/board/{self.board_pk}/post/{self.post_pk}/like/')
            self.assert_http_204_no_content()

    def test_post_serializer(self):
        with self.login(username='user1', password='strong_password_1'):
            self.create_board()
            self.create_post(self.board_pk)

            response = self.get(f'/board/{self.board_pk}/post/{self.post_pk}/')
            res_data = response.data
            self.assertEqual(res_data['author']['username'], 'user1')
            self.assertTrue(res_data['is_author'])
            self.assertFalse(res_data['is_like'])
            self.assertEqual(res_data['title'], 'title')
            self.assertEqual(res_data['content'], 'content')
            self.assertEqual(res_data['like_count'], 0)

        with self.login(username='user2', password='strong_password_2'):
            response = self.get(f'/board/{self.board_pk}/post/{self.post_pk}/')
            res_data = response.data
            self.assertFalse(res_data['is_author'])

            self.post(f'/board/{self.board_pk}/post/{self.post_pk}/like/')
            response = self.get(f'/board/{self.board_pk}/post/{self.post_pk}/')
            res_data = response.data
            self.assertTrue(res_data['is_like'])
            self.assertEqual(res_data['like_count'], 1)
