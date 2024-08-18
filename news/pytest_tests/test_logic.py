from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, pk_news, form_data):
    comment_before = Comment.objects.count()
    url = reverse('news:detail', args=pk_news)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comment_before


def test_user_can_create_comment(author_client, author, pk_news, form_data):
    url = reverse('news:detail', args=pk_news)
    response = author_client.post(url, data=form_data)
    expected_url = f'{url}#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


def test_user_cant_use_bad_words(author_client, pk_news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=pk_news)
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(
        author_client, comment, pk_for_args, pk_news, form_data
):
    url = reverse('news:detail', args=pk_news)
    url_edit = reverse('news:edit', args=pk_for_args)
    expected_url = f'{url}#comments'
    response = author_client.post(url_edit, data=form_data)
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        admin_client, comment, form_data, pk_for_args
):
    url = reverse('news:edit', args=pk_for_args)
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_form_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_form_db.text


def test_author_can_delete_comment(author_client, pk_news, pk_for_args):
    url = reverse('news:detail', args=pk_news)
    url_delete = reverse('news:delete', args=pk_for_args)
    expected_url = f'{url}#comments'
    response = author_client.delete(url_delete)
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        admin_client, comment, pk_for_args
):
    url = reverse('news:delete', args=pk_for_args)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
