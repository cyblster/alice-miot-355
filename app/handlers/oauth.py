from flask import request, redirect, render_template, session, flash
from uuid import uuid4

from app import app, config
from app.forms import RegisterForm, LoginForm
from app.jwt import create_access_token, create_refresh_token, get_payload, is_token_expired
from app.db.utils import (
    verify_password,
    get_user_by_username,
    get_user_by_code,
    add_user,
    update_user_code,
    update_user_refresh_token
)


@app.route('/oauth/register', methods=['GET', 'POST'])
def oauth_register():
    session.pop('_flashes', None)

    form = RegisterForm()
    if form.validate_on_submit():
        if request.form['secret_key'] == config.APP_SECRET:
            user_added = add_user(request.form['username'], request.form['password'])
            if user_added:
                flash('Пользователь успешно зарегистрирован!')
            else:
                flash('Пользователь с таким именем уже существует!')
        else:
            flash('Неверный ключ разработчика!')

    return render_template('register.html', title='Регистрация', form=form,
                           params='?' + '&'.join(f'{k}={v}' for k, v in request.args.items()))


@app.route('/oauth/login', methods=['GET', 'POST'])
def oauth_login():
    session.pop('_flashes', None)

    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)
        if user and verify_password(form.password.data, user['hashed_password']):
            code = uuid4()
            state = request.args['state']
            client_id = request.args['client_id']
            scope = request.args['scope']

            update_user_code(user['username'], code)

            return redirect(f'https://social.yandex.net/broker/redirect?'
                            f'code={code}&state={state}&client_id={client_id}&scope={scope}')

        flash('Неверный логин или пароль!', 'error')

    return render_template('login.html', title='Вход', form=form,
                           params='?' + '&'.join(f'{k}={v}' for k, v in request.args.items()))


@app.route('/oauth/token', methods=['POST'])
def oauth_token():
    code = request.form['code']

    user = get_user_by_code(code)

    access_token, expires_in = create_access_token(user['username'])
    refresh_token = create_refresh_token(user['username'])

    update_user_refresh_token(user['username'], refresh_token)

    return {'access_token': access_token, 'token_type': 'bearer', 'expires_in': expires_in,
            'refresh_token': refresh_token}, 200


@app.route('/oauth/refresh', methods=['POST'])
def oauth_refresh():
    refresh_token = request.form['refresh_token']

    try:
        payload = get_payload(refresh_token)
    except ValueError:
        return 'Invalid token', 403

    if get_user_by_username(payload['sub'])['refresh_token'] != refresh_token:
        return 'Invalid token', 403

    if is_token_expired(payload):
        return 'Expired token', 403

    access_token, expires_in = create_access_token(payload['sub'])
    refresh_token = create_refresh_token(payload['sub'])

    update_user_refresh_token(payload['sub'], refresh_token)

    return {'access_token': access_token, 'token_type': 'bearer', 'expires_in': expires_in,
            'refresh_token': refresh_token}, 200
