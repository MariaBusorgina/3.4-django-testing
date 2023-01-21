import pytest as pytest
from rest_framework.test import APIClient
from model_bakery import baker
from students.models import Course, Student


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def create_course():
    def course_factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return course_factory


@pytest.fixture
def create_student():
    def student_factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return student_factory


# проверка получения 1го курса (retrieve-логика)
@pytest.mark.django_db
def test_create_course(client, create_course):
    messages = create_course(_quantity=10)
    response = client.get('/courses/1/')
    assert response.status_code == 200
    data = response.json()
    assert data.get('name') == messages[0].name


# проверка получения списка курсов (list-логика)
@pytest.mark.django_db
def test_get_list_course(client, create_course):
    messages = create_course(_quantity=10)
    response = client.get('/courses/')
    assert response.status_code == 200
    data = response.json()
    for i, m in enumerate(data):
        assert m['name'] == messages[i].name


# тест успешного создания курса (здесь фабрика не нужна, готовим JSON-данные и создаем курс)
@pytest.mark.django_db
def test_create_new_course(client):
    Course.objects.create(name='Python')
    response = client.get('/courses/')
    assert response.status_code == 200
    data = response.json()[0]['name']
    assert data == 'Python'


# тест успешного обновления курса (сначала через фабрику создаем, потом обновляем JSON-данными)
@pytest.mark.django_db
def test_update_course(client, create_course):
    messages = create_course(_quantity=1)
    request = client.patch('/courses/1/', data={'name': 'S'})
    assert request.status_code == 200
    response = client.get('/courses/')
    assert response.status_code == 200
    data = response.json()[0]['name']
    assert data != messages[0].name


# тест успешного удаления курса
@pytest.mark.django_db
def test_delete_course(client, create_course):
    messages = create_course(_quantity=1)
    request = client.delete('/courses/1/')
    assert request.status_code == 204
    response = client.get('/courses/')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


# проверка фильтрации списка курсов по id (создаем курсы через фабрику, передать id одного курса в фильтр,
# проверить результат запроса с фильтром)
@pytest.mark.django_db
def test_courses_list_filters_id(client, create_course):
    messages = create_course(_quantity=10)
    response = client.get('/courses/?id=1')
    assert response.status_code == 200
    data = response.json()
    assert data[0]['id'] == messages[0].id


# проверка фильтрации списка курсов по name
@pytest.mark.django_db
def test_courses_list_filters_name(client, create_course):
    messages = create_course(_quantity=10)
    search_by_name = messages[0].name
    response = client.get(f'/courses/?name={search_by_name}')
    assert response.status_code == 200
    data = response.json()
    assert data[0]['name'] == search_by_name
