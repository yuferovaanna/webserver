import os

from flask import Flask, session, redirect, render_template, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models import UsersModel, FilmsModel, StoresModel
from forms import LoginForm, RegisterForm, AddFilmForm, SearchPriceForm, SearchStoreForm, AddStoreForm
from db import DB
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db = DB()
UsersModel(db.get_connection()).init_table()
FilmsModel(db.get_connection()).init_table()
StoresModel(db.get_connection()).init_table()


@app.route('/')
@app.route('/index')
def index():
    """
    Главная страница
    :return:
    Основная страница сайта, либо редирект на авторизацю
    """
    # если пользователь не авторизован, кидаем его на страницу входа
    if 'username' not in session:
        return redirect('/login')
    # если админ, то его на свою страницу
    if session['username'] == 'admin':
        return render_template('index_admin.html', username=session['username'])
    # если обычный пользователь, то его на свою
    films = FilmsModel(db.get_connection()).get_all()
    return render_template('film_user.html', username=session['username'], title='Просмотр базы', films=films)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Страница авторизации
    :return:
    переадресация на главную, либо вывод формы авторизации
    """
    form = LoginForm()
    if form.validate_on_submit():  # ввели логин и пароль
        user_name = form.username.data
        password = form.password.data
        user_model = UsersModel(db.get_connection())
        # проверяем наличие пользователя в БД и совпадение пароля
        if user_model.exists(user_name)[0] and check_password_hash(user_model.exists(user_name)[1], password):
            session['username'] = user_name  # запоминаем в сессии имя пользователя и кидаем на главную
            return redirect('/index')
        else:
            flash('Пользователь или пароль не верны')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
def logout():
    """
    Выход из системы
    :return:
    """
    session.pop('username', 0)
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Форма регистрации
    """
    form = RegisterForm()
    if form.validate_on_submit():
        # создать пользователя
        users = UsersModel(db.get_connection())
        if form.user_name.data in [u[1] for u in users.get_all()]:
            flash('Такой пользователь уже существует')
        else:
            users.insert(user_name=form.user_name.data, email=form.email.data,
                         password_hash=generate_password_hash(form.password_hash.data))
            # редирект на главную страницу
            return redirect(url_for('index'))
    return render_template("register.html", title='Регистрация пользователя', form=form)


"""Работа с фильмами"""


@app.route('/film_admin', methods=['GET'])
def film_admin():
    """
    Вывод всей информации об всех автомобилях
    :return:
    информация для авторизованного пользователя
    """
    # если пользователь не авторизован, кидаем его на страницу входа
    if 'username' not in session:
        return redirect('/login')
    # если админ, то его на свою страницу
    if session['username'] != 'admin':
        flash('Доступ запрещен')
        redirect('index')
    # если обычный пользователь, то его на свою
    films = FilmsModel(db.get_connection()).get_all()
    return render_template('film_admin.html',
                           username=session['username'],
                           title='Просмотр фильма',
                           films=films)


@app.route('/add_film', methods=['GET', 'POST'])
def add_film():
    """
    Добавление фильма
    """
    # если пользователь не авторизован, кидаем его на страницу входа
    if 'username' not in session:
        return redirect('login')
    # если админ, то его на свою страницу
    if session['username'] != 'admin':
        return redirect('index')
    form = AddFilmForm()
    available_stores = [(i[0], i[1]) for i in StoresModel(db.get_connection()).get_all()]
    form.store_id.choices = available_stores
    if form.validate_on_submit():
        # создать фильма
        films = FilmsModel(db.get_connection())
        img = form.file.data
        filename = secure_filename(img.filename)
        img.save(os.path.join(app.root_path, 'static', 'img', 'poster', filename))
        films.insert(name=form.name.data,
                     price=form.price.data,
                     store=form.store_id.data,
                     file=filename)
        # редирект на главную страницу
        return redirect(url_for('film_admin'))
    return render_template("add_film.html", title='Добавление фильма', form=form)


@app.route('/film/<int:film_id>', methods=['GET'])
def film(film_id):
    """
    Вывод всей информации об фильме
    :return:
    информация для авторизованного пользователя
    """
    # если пользователь не авторизован, кидаем его на страницу входа
    if 'username' not in session:
        return redirect('/login')
    # если не админ, то его на главную страницу
    '''if session['username'] != 'admin':
        return redirect(url_for('index'))'''
    # иначе выдаем информацию
    film = FilmsModel(db.get_connection()).get(film_id)
    store = StoresModel(db.get_connection()).get(film[3])
    return render_template('film_info.html',
                           username=session['username'],
                           title='Просмотр фильма',
                           film=film,
                           store=store[1])


@app.route('/search_price', methods=['GET', 'POST'])
def search_price():
    """
    Запрос фильмов, удовлетворяющих определенной цене
    """
    form = SearchPriceForm()
    if form.validate_on_submit():
        # получить все машины по определенной цене
        films = FilmsModel(db.get_connection()).get_by_price(form.start_price.data, form.end_price.data)
        # редирект на страницу с результатами
        return render_template('film_user.html', username=session['username'], title='Просмотр базы', films=films)
    return render_template("search_price.html", title='Подбор по цене', form=form)


@app.route('/search_store', methods=['GET', 'POST'])
def search_store():
    """
    Запрос фильмов, продающихся в определенном дилерском центре
    """
    form = SearchStoreForm()
    available_stores = [(i[0], i[1]) for i in StoresModel(db.get_connection()).get_all()]
    form.store_id.choices = available_stores
    if form.validate_on_submit():
        #
        films = FilmsModel(db.get_connection()).get_by_store(form.store_id.data)
        # редирект на главную страницу
        return render_template('film_user.html', username=session['username'], title='Просмотр базы', films=films)
    return render_template("search_store.html", title='Подбор по цене', form=form)


'''Работа с магазином'''


@app.route('/store_admin', methods=['GET'])
def store_admin():
    """
    Вывод всей информации об всех дилерских центрах
    :return:
    информация для авторизованного пользователя
    """
    # если пользователь не авторизован, кидаем его на страницу входа
    if 'username' not in session:
        return redirect('/login')
    # если админ, то его на свою страницу
    if session['username'] != 'admin':
        flash('Доступ запрещен')
        redirect('index')
    # иначе это админ
    stores = StoresModel(db.get_connection()).get_all()
    return render_template('store_admin.html',
                           username=session['username'],
                           title='Просмотр магазинов',
                           stores=stores)


@app.route('/store/<int:store_id>', methods=['GET'])
def store(store_id):
    """
    Вывод всей информации о дилерском центре
    :return:
    информация для авторизованного пользователя
    """
    # если пользователь не авторизован, кидаем его на страницу входа
    if 'username' not in session:
        return redirect('/login')
    # если не админ, то его на главную страницу
    if session['username'] != 'admin':
        return redirect(url_for('index'))
    # иначе выдаем информацию
    store = StoresModel(db.get_connection()).get(store_id)
    return render_template('store_info.html',
                           username=session['username'],
                           title='Просмотр информации о магазине',
                           store=store)


@app.route('/add_store', methods=['GET', 'POST'])
def add_store():
    """
    Добавление магазина и вывод на экран информации о нем
    """
    # если пользователь не авторизован, кидаем его на страницу входа
    if 'username' not in session:
        return redirect('/login')
    # если админ, то его на свою страницу
    if session['username'] == 'admin':
        form = AddStoreForm()
        if form.validate_on_submit():
            # создать магазина
            stores = StoresModel(db.get_connection())
            stores.insert(name=form.name.data, address=form.address.data)
            # редирект на главную страницу
            return redirect(url_for('index'))
        return render_template("add_store.html", title='Добавление магазина', form=form)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
