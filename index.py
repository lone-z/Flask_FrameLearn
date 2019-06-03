# -*- encoding: utf-8 -*-
from flask import *
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Manager, Migrate, MigrateCommand

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
app.secret_key = 'H1812B'

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


''' 管理员表 '''
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String(50), nullable = False)
    pwd = db.Column(db.String(128), nullable = False)
''' 用户表 '''
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.String(50), nullable = False)
    pwd = db.Column(db.String(128),nullable = False)


''' 作者表 '''
class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100),nullable = False)
    books = db.relationship(
        'Books', backref ='author', lazy='dynamic', cascade='all, delete-orphan', )
''' 书籍表 '''
class Books(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200))
    price = db.Column(db.DECIMAL(10,2), default = 999999)
    content = db.Column(db.Text)
    count = db.Column(db.Integer, default = 1)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id', ondelete = 'CASCADE'))


''' 购物车表 '''
class Shopping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    books_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    count = db.Column(db.Integer,default=1)


''' 建表、删表 '''
@app.route('/cre_del')
def cre_del():
    # db.drop_all()
    db.create_all()
    return '数据表新建成功'



# 管理员注册
@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        if request.form.get('reg') is not None:
            name = request.form.get('name')
            pwd1 = request.form.get('pwd1')
            pwd2 = request.form.get('pwd2')
            if all([name, pwd1, pwd2]):
                if pwd1 == pwd2:
                    if Admin.query.filter(Admin.user == name).first():
                        flash('用户名已存在')
                    else:
                        admin = Admin()
                        admin.user =  name
                        admin.pwd = pwd1
                        db.session.add(admin)
                        db.session.commit()
                        flash('注册成功')
                        redirect(url_for('admin_login'))
                else:
                    flash('密码输入不一致')
            else:
                flash('信息输入不完整')
        # elif request.form.get('log') is not None:
        else:
            return redirect(url_for('admin_login'))

    return render_template('admin/register.html')


# 管理员登陆
@app.route('/admin/login', methods = ['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('log') is not None:
            name = request.form.get('name')
            pwd = request.form.get('pwd')
            if all([name, pwd]):
                a = Admin.query.filter(Admin.user == name).first()
                if a:
                    if a.pwd == pwd:
                        session['user_id'] = a.id
                        flash('登陆成功')
                        return redirect(url_for('admin'))
                    else:
                        flash('密码错误')
                else:
                    flash('用户名错误')
            else:
                flash('信息不全')
        else:
            return redirect(url_for('admin_register'))
    return render_template('admin/login.html')



# 管理员首页 及 添加作者和图书
@app.route('/admin', methods = ['GET', 'POST'])
def admin():
    if request.method == 'POST':
        author_name = request.form.get('author')
        book_name = request.form.get('book')
        if all([author_name,book_name]):
            a = Author.query.filter(Author.name == author_name).first()
            if a :
                if book_name in [b.name for b in a.books]:
                    flash('该书籍已存在')
                else:
                    book =Books()
                    book.name = book_name
                    a.books.append(book)
                    db.session.add(a)
                    db.session.commit()
                    flash('书籍添加成功')
            else:	# 作者不存在
                author = Author()
                author.name = author_name

                book = Books()
                book.name = book_name
                author.books.append(book)

                db.session.add(author)
                db.session.commit()
                flash('新作者书籍添加成功')
        else:
            flash('信息不全')

    d = {}
    author_list = Author.query.all()
    d['a_list'] = author_list
    return render_template('admin/index.html', data=d)


# 管理员修改作者
@app.route('/admin/change_author/<id>', methods = ['GET', 'POST'])
def Admin_ChangeAuthor(id):
    d = {}
    a = Author.query.get(id)
    d['author_info'] = a
    if request.method == 'POST':
        if request.form.get('aut'):
            author_name = request.form.get('author')
            if all([author_name]):
                author = Author.query.filter(Author.name == author_name).first()
                # 当作者存在，且作者不为
                if author and Author.name != a.name:
                    flash('名字未修改')
                    return redirect((url_for('admin')))
                else:
                    a.name = author_name
                    db.session.commit()
                    return redirect(url_for('admin'))
            else:
                flash('姓名不能为空')
    return render_template('admin/change_author.html', data=d)


# 管理员修改书籍
@app.route('/admin/change_book/<id>', methods = ['GET', 'POST'])
def adimn_ChangeBooks(id):
    d = {}
    book = Books.query.get(id)
    d['book_info'] = book

    if request.method == 'POST':
        if request.form.get('bok') is not None:
            book_name = request.form.get('book')
            if all([book_name]):
                # book = Books.query.filter(Books.name == book_name).first()
                # if book:
                if book_name in [b.name for b in book.author.books]:
                    flash('书名重复')
                else:
                    book.name = book_name
                    db.session.commit()
                    return redirect(url_for('admin'))
            else:
                flash('信息不全')
    return render_template('admin/change_book.html', data=d)


# 管理员删除作者
@app.route('/admin/del_author/<id>', methods= ['GET' , 'POST'])
def del_author(id):
    try:
        a = Author.query.get(id)
        db.session.delete(a)
        db.session.commit()
    except:
        flash('删除失败')
    return redirect(url_for('admin'))


# 管理员删除书籍
@app.route('/admin/del_book/<id>')
def del_book(id):
    try:
        a = Books.query.get(id)
        db.session.delete(a)
        db.session.commit()
    except:
        flash('删除失败')
    return redirect(url_for('admin'))


# 前台逻辑
@app.route('/', methods=['GET', 'POST'])
def index():
    d = {}
    author_list = Author.query.all()

    ## 修改原始数据，控制作者名下书籍的数量（后台方法）
    # for a in author_list:
    #     a.books = a.books.limit(1)

    d['author_list'] = author_list
    return render_template('user/index.html', data= d)


# 商品详情
@app.route('/user/dict')
def detail():
    d = {}
    books_list = Books.query.all()
    d['book_list'] = books_list
    user_id = session.get('user_id') # 通过session 中是否存在 user_id 来判断用户是否登陆
    if user_id:
        user = User.query.get(user_id)
        d['user_info'] = user
    else:
        d['user_info'] = None
    return render_template('user/index.html', data=d)


# 用户注册
@app.route('/user/register', methods = ['GET', 'POST'])
def U_register():
    if request.method == 'POST':
        # 如果用户点击的是登陆按钮,跳转到登陆接口
        if request.form.get('log') is not None:
            return redirect(url_for('U_login'))
        else:
            # '注册逻辑'
            name = request.form.get('user')
            pwd = request.form.get('pwd')
            pwd2 = request.form.get('pwd2')
            if all([name, pwd, pwd2]):
                # 判断两次密码是否一致
                if pwd ==pwd2:
                    # 用户名是否存在
                    u = User.query.filter(User.user == name).first()
                    if u:
                        flash('用户名已存在，请更换用户名')
                    else:
                        user = User()
                        user.user = name
                        user.pwd = pwd
                        db.session.add(user)
                        db.session.commit()
                        flash('注册成功')
                        return redirect(url_for('U_login'))
                else:
                    flash('两次密码输入不一致')
            else:
                # 用户输入信息不完整
                flash('信息不完整')
    return render_template('user/register.html')


# 用户登陆
@app.route('/user/login', methods = ['GET', 'POST'])
def U_login():
    if request.method == 'POST':
        user = request.form.get('user')
        pwd = request.form.get('pwd')
        if all([user, pwd]):
            u = User._query.filter(User.user == user).first()
            if u:
                if User.pwd == pwd:
                    session['user_id'] = u.id
                    flash('登陆成功')
                    return redirect(url_for('index'))
                else:
                    flash('密码错误')
            else:
                flash('用户名不存在')
        else:
            flash('请输入完整信息')
    return render_template('user/login.html')


if __name__ == '__main__':
    app.run()
    # manager.run()
