from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Teкст комментария',
        author=author,
        news=news
    )
    return comment


@pytest.fixture
def pk_for_args(comment):
    return (comment.pk,)


@pytest.fixture
def pk_news(news):
    return (news.pk,)


@pytest.fixture
def all_news():
    today = datetime.today()
    news_list = [
        News(
            title=f'Новость {index}',
            text='Текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    all_news = News.objects.bulk_create(news_list)
    return all_news


@pytest.fixture
def form_data():
    return {
        'text': 'Текст нового комментария'
    }
