from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret" 
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:justblogit@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'as9d8F7d98C3f7a'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    submitted = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, submitted=True):
        self.title = title
        self.body = body
        self.submitted = submitted
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = relationship("Blog", backref="user")


    def __init__(self, username, password, blogs):
        self.username = username
        self.password = password
        self.blogs = blogs

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def home():
    blog_id = request.args.get('id')
    submitted_blogs = Blog.query.all()
    return render_template('login.html', submitted_blogs=submitted_blogs)

@app.route('/index', methods=['POST', 'GET'])
def index():
    all_users = User.query.all()
    #blog_id = request.args.get('id')
    return render_template('index.html', all_users=all_users)


    """blog_id = request.args.get('id')
    submitted_blogs = Blog.query.all()
    return render_template('index.html', submitted_blogs=submitted_blogs)"""

@app.route('/blog', methods=['POST', 'GET'])
def show_posts(): 
    
    if "id" in request.args:
        id = request.args.get('id')
        entry = Blog.query.get(id)
        
        return render_template('blog.html', title = entry.title, body = entry.body, owner = entry.owner)

    if "user" in request.args:
        submitted_blogs = Blog.query.all()
        owner_id = request.args.get('user')
        user_submitted_blogs = Blog.query.filter_by(owner_id=owner_id)
        username = User.query.filter_by(owner_id=owner_id)

        return render_template('index.html', page_title = "User Contributions", user_submitted_blogs=user_submitted_blogs, user=username)


    if request.method == 'GET':
        submitted_blogs = Blog.query.all()
        return render_template('blog.html', submitted_blogs=submitted_blogs, title=title, body=body)

    return render_template('blog.html', submitted_blogs=submitted_blogs, user_submitted_blogs=user_submitted_blogs)

@app.route('/landing', methods =['GET'])
def show_blog():
    blog_id = request.args.get('id')
    blog = Blog.query.get(blog_id)
    return render_template('landing.html', blog=blog)
    

# @app.route('/newpost', methods=['POST', 'GET'])
# def test():
#     user_id = '' 
#     if request.method == 'POST':
#         user_id = db.session.query(User.id).filter_by(username=request.form['username'] )  
#         flash(user_id)
#         return render_template('test.html', user_id=user_id)
#     else:
#          return render_template('newpost.html', title='title', body='body')

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    title = ''
    body = ''
    username = session['username']    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']    
        submitted = True        
        owner_id = request.args.get(username)
        #print("username:" + username)
        user_id = User.query.filter_by(id=id)
        #flash("user:", user)
        #user_id = db.session.query(User.id).filter_by(username=request.form['username']).get()
        #flash(user_id)
        owner_id = User.query.filter_by(username=username).first()
        #owner_id = user_id
        newpost = Blog(title=title, body=body, submitted=True, owner_id=owner_id)
        db.session.add(newpost)
        db.session.commit()
        # blog=newpost.id
        # blogs=Blogs(title=title, body=body)
        return redirect('/blog?id={0}'.format(blog))
    else:
        return render_template('newpost.html', title='title', body='body', username=username)


"""
New Routes Below
"""

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")        
            return redirect('/newpost')    
        else:
            flash('Error: User password incorrect, or user does not exist')
            return redirect('/login')    
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        blogs = []
        # TODO - validate user's data
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password, blogs)
            db.session.add(new_user)
            db.session.commit()
            user=new_user.id
            session['username'] = username
            #return redirect('/user?id={0}'.format(user))
            return redirect('/newpost')
        else:
            return "<h1>Duplicate user</h1>"
        error = []
        if len(username) < 3:
            flash('Username must be between 3 and 30 characters')
            return redirect('/')
        if password != verify:
            flash('Passwords must match')
            return redirect('/signup')
        if len(username) < 1 or len(password) < 1 or len(verify) < 1:
            flash('You must complete the information from all fields')
            return redirect('/')
        for char in username or char in email or char in password:
            if char == " ":
                flash('Invalid character: Your password may not contain a space')
                return redirect('/')                
        if len(username) <3 or len(password) < 3 or len(username) > 20 or len(password) > 20:
            flash('Username and Password must be between 3-20 characters')
            return redirect('/signup')            
        else:
            session['username'] = username 
            flash("Welcome", + username)
            return redirect('/blog')
    return render_template('signup.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')
# @app.route('/delete-entry', methods=['POST'])
# def delete_entry():

#     blog_id = int(request.form['entry-id'])
#     entry = Blog.query.filter_by(title)
#     Blog.completed = False
#     db.session.delete(entry)
#     db.session.commit()

#     return redirect('/')


if __name__ == '__main__':
    app.run()

