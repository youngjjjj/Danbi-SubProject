from test_plus import APITestCase

from board.models import Boards, Post, Comment


class CommentAPITestcase(APITestCase):

    def setUp(self):
        self.user1 = self.make_user(username='user1', password='strong_password_1')
        self.user2 = self.make_user(username='user2', password='strong_password_2')
        self.board_pk = 0
        self.post_pk = 0
        self.comment_pk = 0

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

    def create_comment(self, board_pk, post_pk):
        self.post(f'/board/{board_pk}/post/{post_pk}/comment/', data={
            'text': 'text',
        })
        self.comment_pk += 1

    def test_comment_model(self):
        board = Boards.objects.create(author=self.user1, title='board_title')
        post = Post.objects.create(author=self.user1, board=board, title='post_title', content='post_content')
        comment = Comment.objects.create(author=self.user1, post=post, text='comment_text')
        self.assertEqual(str(comment), 'user1님이 작성한 댓글 comment_text 입니다.')

    def test_comment_create(self):
        self.create_board()
        self.create_post(board_pk=self.board_pk)
        self.create_comment(board_pk=self.board_pk, post_pk=self.post_pk)
        self.assert_http_403_forbidden()
        is_comment = Comment.objects.exists()
        self.assertFalse(is_comment)

        with self.login(username='user1', password='strong_password_1'):
            self.create_board()
            self.create_post(board_pk=self.board_pk-1)
            self.create_comment(board_pk=self.board_pk-1, post_pk=self.post_pk-1)
            self.assert_http_201_created()
            is_comment = Comment.objects.exists()
            self.assertTrue(is_comment)

    def test_comment_get(self):
        with self.login(username='user1', password='strong_password_1'):
            self.create_board()
            self.create_post(board_pk=self.board_pk)
            self.create_comment(board_pk=self.board_pk, post_pk=self.post_pk)
            self.get_check_200(f'/board/{self.board_pk}/post/{self.post_pk}/comment/')
            self.get_check_200(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/')

        self.get(f'/board/{self.board_pk}/post/{self.post_pk}/comment/')
        self.assert_http_403_forbidden()
        self.get(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/')
        self.assert_http_403_forbidden()

    def test_comment_update(self):
        with self.login(username='user1', password='strong_password_1'):
            self.create_board()
            self.create_post(board_pk=self.board_pk)
            self.create_comment(board_pk=self.board_pk, post_pk=self.post_pk)
            self.put(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/', data={
                'text': 'fix_test',
            })
            self.assert_http_200_ok()

        with self.login(username='user2', password='strong_password_2'):
            self.put(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/', data={
                'text': 'fix_second_test',
            })
            self.assert_http_403_forbidden()
            comment = Comment.objects.first()
            self.assertEqual(comment.text, 'fix_test')

        self.put(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/', data={
            'text': 'fix_third_test',
        })
        self.assert_http_403_forbidden()

    def test_comment_delete(self):
        with self.login(username='user1', password='strong_password_1'):
            self.create_board()
            self.create_post(board_pk=self.board_pk)
            self.create_comment(board_pk=self.board_pk, post_pk=self.post_pk)

        with self.login(username='user2', password='strong_password_2'):
            self.delete(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/')
            self.assert_http_403_forbidden()
            is_comment = Comment.objects.exists()
            self.assertTrue(is_comment)

        self.delete(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/')
        self.assert_http_403_forbidden()
        is_comment = Comment.objects.exists()
        self.assertTrue(is_comment)

        with self.login(username='user1', password='strong_password_1'):
            self.delete(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/')
            self.assert_http_204_no_content()
            is_comment = Comment.objects.exists()
            self.assertFalse(is_comment)

    def test_comment_like_create(self):
        with self.login(username='user1', password='strong_password_1'):
            self.create_board()
            self.create_post(board_pk=self.board_pk)
            self.create_comment(board_pk=self.board_pk, post_pk=self.post_pk)
            self.post(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/like/')
            self.assert_http_201_created()
            comment = Comment.objects.first()
            like_count = comment.like_comment.count()
            self.assertEqual(like_count, 1)
            self.post(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/like/')
            self.assert_http_400_bad_request()

        self.post(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/like/')
        self.assert_http_403_forbidden()
        comment = Comment.objects.first()
        like_count = comment.like_comment.count()
        self.assertEqual(like_count, 1)

        with self.login(username='user2', password='strong_password_2'):
            self.post(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/like/')
            self.assert_http_201_created()
            comment = Comment.objects.first()
            like_count = comment.like_comment.count()
            self.assertEqual(like_count, 2)

    def test_comment_like_get(self):
        self.post(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/like/')

        with self.login(username='user1', password='strong_password_1'):
            self.create_board()
            self.create_post(board_pk=self.board_pk)
            self.create_comment(board_pk=self.board_pk, post_pk=self.post_pk)
            self.get(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/like/')
            self.assert_http_400_bad_request()

        with self.login(username='user2', password='strong_password_2'):
            self.post(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/like/')
            self.get(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/like/')
            self.assert_http_200_ok()

        self.get(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/like/')
        self.assert_http_403_forbidden()

    def test_comment_like_delete(self):
        with self.login(username='user1', password='strong_password_1'):
            self.create_board()
            self.create_post(board_pk=self.board_pk)
            self.create_comment(board_pk=self.board_pk, post_pk=self.post_pk)
            self.post(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/like/')

        self.delete(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/like/')
        self.assert_http_403_forbidden()
        comment = Comment.objects.first()
        like_count = comment.like_comment.count()
        self.assertEqual(like_count, 1)

        with self.login(username='user2', password='strong_password_2'):
            self.delete(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/like/')
            self.assert_http_400_bad_request()
            comment = Comment.objects.first()
            like_count = comment.like_comment.count()
            self.assertEqual(like_count, 1)

        with self.login(username='user1', password='strong_password_1'):
            self.delete(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/like/')
            self.assert_http_204_no_content()
            comment = Comment.objects.first()
            like_count = comment.like_comment.count()
            self.assertEqual(like_count, 0)

    def test_comment_serializer(self):
        with self.login(username='user1', password='strong_password_1'):
            self.create_board()
            self.create_post(board_pk=self.board_pk)
            self.create_comment(board_pk=self.board_pk, post_pk=self.post_pk)

            res = self.get(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/')
            res_data = res.data
            self.assertEqual(res_data['author']['username'], 'user1')
            self.assertTrue(res_data['is_author'])
            self.assertFalse(res_data['is_like'])
            self.assertEqual(res_data['text'], 'text')
            self.assertEqual(res_data['like_count'], 0)

        with self.login(username='user2', password='strong_password_2'):
            res = self.get(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/')
            res_data = res.data
            self.assertFalse(res_data['is_author'])

            self.post(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/like/')
            res = self.get(f'/board/{self.board_pk}/post/{self.post_pk}/comment/{self.comment_pk}/')
            res_data = res.data
            self.assertTrue(res_data['is_like'])
            self.assertEqual(res_data['like_count'], 1)

