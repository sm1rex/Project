from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['UPLOAD_FOLDER']='newBlog/static/uploads/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newBlog.db'
app.config['SECRET_KEY'] = 'UDGFXESCRDFodiywtf8e9wfogew80'

db = SQLAlchemy(app)
login_manager = LoginManager() 
login_manager.init_app(app)
login_manager.login_view = 'login'
#gut


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False) # String can be limited for exmpl db.String(50), maximum of 50 characters, while Text can't be limited
    image_path = db.Column(db.String(200))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    avatar_path = db.Column(db.String(200), nullable=True)

# how to save and creat tables without Base import
with app.app_context():
    db.create_all()
# ez lol fr

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


#CRUD - create, read, update, delete

def get_posts():
    return Post.query.all()


def add_post(title, content, image=None):
    image_path=None
    if image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(image_path)
    post = Post(title = title, content=content, image_path=image_path)
    db.session.add(post)
    db.session.commit()



def delete_post(post_id):
    post = Post.query.get(post_id)
    if post:
        db.session.delete(post)
        db.session.commit()



def edit_post(post_id, title, content, image=None):
    post = Post.query.get(post_id)
    if post:
        post.title = title
        post.content = content
        if image:
            post.image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(post.image_path)
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        search_term = request.form['search']
        posts = Post.query.filter(Post.title.like(f'%{search_term}%') | Post.content.like(f'%{search_term}%')).all()
        return render_template('index.html', posts=posts)
    else:
        posts = get_posts()
    return render_template('index.html', posts=posts)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']
        image = request.files['image']
        add_post(title, content, image)
        return redirect( url_for('index'))
    else:
        return render_template('add.html')

@app.route('/delete/<int:post_id>')
def delete(post_id):
    delete_post(post_id)
    return redirect(url_for('index'))

@app.route('/edit/<int:post_id>', methods=["GET", "POST"])
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']
        image = request.files['image']
        edit_post(post_id, title, content, image)
        return redirect(url_for('index'))
    else:
        return render_template('edit.html', post=post)


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('User was not found or you have made a mistake in password or email. ')
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])                                                                                                                                                                                         
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        icon = request.files['icon']
        
        hash_password = generate_password_hash(password)
        icon_path = None
        if icon:
            icon_path = os.path.join('newBlog/static/usericons/', icon.filename)
            icon.save(icon_path)
        
        new_user = User(email=email, username=username, password=hash_password, avatar_path=icon_path)
        db.session.add(new_user)
        db.session.commit()
        flash('Registered succesful! Please login!')
        return redirect(url_for('login'))
    else:
        return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)                     