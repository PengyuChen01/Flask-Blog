import pytest
from flask import g, session
from flaskr.db import get_db

#in the client register page type username and password with 'a'
def test_register(client, app):
     #Access the registration page and check if it's available (status code 200)
    assert client.get('/auth/register').status_code == 200
    # Submit the registration form with the username and password both set to 'a'
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    # After successful registration, ensure the user is redirected to the login page
    assert response.headers["Location"] == "/auth/login"
    # Using the app's context, check if the user with username 'a' has been added to the database
    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None

# Parametrize a test to run with different inputs and expected outputs
# This checks various scenarios like missing username, missing password, and already registered user
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'), # missing username
    ('a', '', b'Password is required.'), #missing password
    ('test', 'test', b'already registered'), #user exist
))
#after user regist, get username and password he typed in
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data


# Test the user login process on the main page
def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    # Use the auth fixture to simulate a login attempt
    response = auth.login()
     # After a successful login, ensure the user is redirected to the main page
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        # new session is created
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
# Test function to validate user login input
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

#user log out session, session should be contain user id after logging out
def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session

import pytest
from flaskr.db import get_db


def test_index(client, auth):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data

@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404

def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': ''})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data

def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None

