import pytest
from django.conf import settings
from django.urls import reverse


pytestmark = pytest.mark.django_db


def test_count_news(client, all_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert object_list is not None
    news_list = object_list.count()
    assert news_list <= settings.NEWS_COUNT_ON_HOME_PAGE


def test_order_news(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert object_list is not None
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates


def test_order_comments(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert sorted_timestamps == all_timestamps


@pytest.mark.parametrize(
    'parametrized_client, form_in_page',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
def test_form_availability_for_different_users(
        news, parametrized_client, form_in_page
):
    url = reverse('news:detail', args=(news.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_in_page
