from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
#Armen Juhl
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret" 
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:justblogit@localhost:8889/blogz'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz2:blogz@localhost:8889/blogz2'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'as9d8F7d98C3f7a'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    submitted = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    def __init__(self, title, body, submitted,owner):
        self.title = title
        self.body = body
        self.submitted = submitted
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref = 'owner')


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
    #blog_id = request.args.get('id')
    all_users = User.query.all()
    return render_template('index.html', all_users=all_users)


    """blog_id = request.args.get('id')
    submitted_blogs = Blog.query.all()
    return render_template('index.html', submitted_blogs=submitted_blogs)"""
@app.route('/blog', methods=["POST", "GET"])
def list_blogs():
    # define variable using database query
    submitted_blogs = Blog.query.all()

    # redirects to single blog entry when blog title is clicked
    if "id" in request.args:
        id = request.args.get('id')
        entry = Blog.query.get(id)
        
        return render_template('blog.html', title = entry.title, body = entry.body, owner = entry.owner)

    # redirects to page showing all blog entries for a specific user when user name is clicked
    if "user" in request.args:
        submitted_blogs = Blog.query.all()
        owner_id = request.args.get('user')
        user_submitted_blogs = Blog.query.filter_by(owner_id=owner_id)
        username = User.query.filter_by(owner_id=owner_id)

        return render_template('index.html', page_title = "User Contributions", user_submitted_blogs=user_submitted_blogs, user=username)

    # displays template posts which displays all entries in descending order
    return render_template('blog.html', submitted_blogs=submitted_blogs, user_submitted_blogs=user_submitted_blogs)

@app.route('/blog', methods=['POST', 'GET'])
def show_posts(): 
    if request.method == 'GET':
        submitted_blogs = Blog.query.all()
    title = ''
    body = ''
    if "id" in request.args:
        id = request.args.get('id')
        entry = Blog.query.get(id)
    
        return render_template('blog.html', submitted_blogs=submitted_blogs, title=title, body=body)
    return render_template('landing.html', page_title="blog-post", title = entry.title, body = entry.body, owner = entry.owner)

 
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


@app.route('/newpost', methods=["POST", "GET"])
def add_entry():
    
    # render newpost template
    if request.method == "GET":
        return render_template('newpost.html', page_title="blog")

    # define variables using form entries
    title = request.form["title"]
    body = request.form["body"]

    # verification that title is filled in
    if title == "":
        title_error = "Blog entry must have a title."
    else:
        title_error = "" 

    # verification that body is filled in
    if body == "":
        body_error = "Blog entry must have content."
    else:
        body_error = ""
    
    # if there are no errors, adds new entry to the database and redirects user to entries template
    if not title_error and not body_error:
        if request.method == "POST":
            submitted = True
            owner= User.query.filter_by(username =session['username']).first()
            newpost = Blog(title=title, body=body, submitted=True,owner=owner)
            db.session.add(newpost)
            db.session.commit()
        
        return render_template('blog.html', page_title = "confirmation", title = title, body = body, owner = owner)
    else:
        # re-renders newpost template with appropriate error messages if errors exist
        return render_template('newpost.html', page_title = "blog", title = title, 
            title_error = title_error, body = body, body_error = body_error)


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
        blogs = ['']
        # TODO - validate user's data
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            user=new_user.id
            session['username'] = username
            #return redirect('/user?id={0}'.format(user))
            return redirect('/newpost')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"
        error = ''
        if len(username) < 3:
            flash('Username must be between 3 and 30 characters')
            return redirect('/')
        if password != verify_password:
            flash('Passwords must match')
            return redirect('/signup')
        if len(username) < 1 or len(password) < 1 or len(verify_password) < 1 or len(email) < 1:
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



if __name__ == '__main__':
    app.run()
