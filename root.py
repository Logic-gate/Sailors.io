import os
import datetime
from flask import Flask, request, flash, url_for, redirect, \
     render_template, abort, send_from_directory, Markup
from flask_mail import Mail, Message
import urllib2
import re
import random
import feedparser
from bs4 import BeautifulSoup
from ascii_graph import Pyasciigraph
from selenium import webdriver
from tabulate import tabulate
import pythonwhois
from functools import wraps
from werkzeug.security import generate_password_hash
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient
import time
from flask import Flask
from flask.ext.login import LoginManager
from flask import request, redirect, render_template, url_for, flash, g
from flask.ext.login import login_user, logout_user, login_required, current_user
from forms import LoginForm, SignupForm, PostForm, EditForm, ProfileForm, Comments, QuickPost
from user import User
from itsdangerous import URLSafeTimedSerializer
from flask.ext.misaka import Misaka
from flask.ext.pagedown import PageDown
from bson.objectid import ObjectId
from flask.ext.paginate import Pagination
from link import Meta
from imgur import Imgur
from werkzeug import secure_filename
import json




# GLOBALS
app = Flask(__name__)
app.config.from_pyfile('root.cfg')
lm = LoginManager()
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['MAX_CONTENT_LENGTH'] = 1024000
lm.init_app(app)
lm.login_view = 'login'
mail = Mail(app)
Misaka(app)
pagedown = PageDown(app)




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def home():
    return redirect(url_for('posts'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = app.config['USERS_COLLECTION'].find_one({"_id": form.username.data})
        if user and User.validate_login(user['password'], form.password.data):
            user_obj = User(user['_id'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            next = request.args.get('next')
            return redirect(next or url_for("posts"))
        flash("Wrong username or password!", category='error')
    return render_template('login.html', title='login', form=form, signup_form=SignupForm())




@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('posts'))


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email



@app.route('/signup',  methods=['GET', 'POST'])
def signup():
    signup_form = SignupForm()
    if request.method == 'POST' and signup_form.validate_on_submit():
        collection = app.config['USERS_COLLECTION']
        user = signup_form.username_signup.data
        password = signup_form.password_signup.data
        email = signup_form.email.data
        subject = "Please confirm your email"
        pass_hash = generate_password_hash(password, salt_length=10)
        try:
            if not app.config['USERS_COLLECTION'].find_one({"email": email}):
                collection.insert({"_id": user, "password": pass_hash, "email": email, "confirmed": False, "bio": "Ahoy Captain"})
                token = generate_confirmation_token(email)
                confirm_url = url_for('confirm_email', token=token, _external=True)
                html = render_template('confirm_email.html', confirm_url=confirm_url)
                flash("Please confirm your email to login", category='success')
                send_email(email, subject, html)
                return redirect(request.args.get("next") or url_for("write"))
            else:
                flash("Email already in use", category='error')
        except DuplicateKeyError:
            flash("Username already in use", category='error')
    return render_template('login.html', title='signup', form=LoginForm(), signup_form=signup_form)



@app.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    post_form = PostForm()
    if request.method == 'POST':
        collection = app.config['POSTS_COLLECTION']
        post = post_form.post.data
        user = current_user.get_id()
        tags = post_form.tags.data.split(',')
        title = post_form.post_title.data

        try:

            collection.insert({"title": title, "entry":post, "user":user, "created_on": datetime.datetime.now(), "tags": tags})
            return redirect(url_for("posts"))
        except:
            flash("Something went bad....", category='error')
    return render_template('write.html', form=post_form)



def get_tweet(tweetid):
    url = 'https://api.twitter.com/1/statuses/oembed.json?id=%s' %tweetid
    open_ = urllib2.urlopen(url)
    return json.loads(open_.read())


def handle_posts(url):
    regex_youtube =  re.compile(r'^(?:http)s?://(?:youtube.com|www.youtube.com)')
    regex_imgur =  re.compile(r'^(?:http)s?://(?:imgur.com)')
    regex_twitter =  re.compile(r'^(?:http)s?://(?:twitter.com)')
    user = current_user.get_id()
    collection = app.config['POSTS_COLLECTION']
    tags = ['External', 'Link']
    try:
        link = Meta(url)
        content = link.get_global_meta()
    except:
        link = url
        content = ('External Link', '')
    if regex_youtube.findall(url):
        entry_make = "<iframe width='560' height='315' src='https://www.youtube.com/embed/%s' frameborder='0' allowfullscreen></iframe>" %url.split('v=')[1]
    elif regex_imgur.findall(url):
        entry_make = '<blockquote class="imgur-embed-pub" lang="en" data-id="%s"><a href="//imgur.com/%s">View post on imgur.com</a></blockquote><script async src="//s.imgur.com/min/embed.js" charset="utf-8"></script>' %(url.split('/')[4], url.split('/')[4])
    elif regex_twitter.findall(url):
        t = get_tweet(url.split('/')[5])
        entry_make = t['html']
        content = ('Twitter', '')
        tags = ['External', 'Twitter']
    else:
        entry_make = "<h4>%s</h4><br><h6><a href='%s' target='_blank'>%s</a></h6>" %(content[0], url, url)
    try:
        collection.insert({"title": content[0], "entry":entry_make, "user":user, "created_on": datetime.datetime.now(), "tags": tags})
    except:
        flash("Something went bad....", category='error')


@app.route('/posts', methods=['GET', 'POST'])
def posts():
    form = QuickPost()
    url = form.link.data
    regex_http = re.compile(r'^(?:http|ftp)s?://')
    if request.method == 'POST' and request.files['file']:
        file = request.files['file']
        if file and allowed_file(file.filename):
            collection = app.config['POSTS_COLLECTION']
            filename = secure_filename(file.filename)
            g = os.path.join(app.config['DIR_PATH'], app.config['UPLOAD_FOLDER'])
            sav = file.save(os.path.join(g, filename))
            user = current_user.get_id()
            _id = app.config['IMGUR_ID']
            _secret = app.config['IMGUR_SECRET']
            tags = ['External', 'Imgur']
            try:
                img = Imgur(_id, _secret)
                f = img.Image_Upload(os.path.join(g, filename))
                entry_make = "<img src=%s><br><a href='%s' target='_blank'>%s</a>" %(f['link'], f['link'], f['link'])
                try:
                    collection.insert({"title": f['id'], "entry":entry_make, "user":user, "created_on": datetime.datetime.now(), "tags": tags})
                    os.remove(os.path.join(g, filename))
                    print 'file deleted'
                except: 
                    flash("Something went bad....", category='error')
            except:
                flash("Something went bad...on imgur", category='error')

    if request.method == 'POST' and regex_http.findall(url):
        if current_user.is_authenticated() and url != None:
            handle_posts(url)
            




    page, per_page, offset = get_page_items()
    count = app.config['POSTS_COLLECTION'].find().sort(u'_id', -1).count()
    p = app.config['POSTS_COLLECTION'].find().sort(u'_id', -1).limit(per_page).skip(offset)
   
    pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=count,
                                record_name='posts')
    return render_template('posts.html', posts=p, pagination=pagination, form=form)


def get_pagination(**kwargs):
    kwargs.setdefault('record_name', 'records')
    return Pagination(css_framework='bootstrap3',
                      show_single_page=False,
                      **kwargs
                      )


def get_page_items():
    page = int(request.args.get('page', 1))
    per_page = request.args.get('per_page')
    if not per_page:
        per_page = 10
    else:
        per_page = int(per_page)

    offset = (page - 1) * per_page
    return page, per_page, offset


@app.route('/by_tag/<tag>')
def by_tag(tag):
    form = QuickPost()
    if tag:
        page, per_page, offset = get_page_items()
        count = app.config['POSTS_COLLECTION'].find({"tags": tag}).sort(u'_id', -1).count()
        p = app.config['POSTS_COLLECTION'].find({"tags": tag}).sort(u'_id', -1).limit(per_page).skip(offset)
       
        pagination = get_pagination(page=page,
                                    per_page=per_page,
                                    total=count,
                                    record_name='posts')
        return render_template('posts.html', posts=p,  pagination=pagination, form=form)
    else:
        flash("No tags founds", category='error')
        return redirect(url_for('posts'))



@app.route('/confirm/<token>')
@login_required
def confirm_email(token):

    collection = app.config['USERS_COLLECTION']
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user = app.config['USERS_COLLECTION'].find({"email": email})
    obj = next(user, None)
    if obj['confirmed'] == True:
        flash('Account already confirmed. Please login.', 'success')
    else:
        collection.update_one({"email": email}, {"$set":{"confirmed": True, "confirmed_on": datetime.datetime.now()}})
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('main_page'))


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)

@app.route('/user/<nickname>')
def user(nickname):
    page, per_page, offset = get_page_items()
    user = current_user.get_id()
    count = app.config['POSTS_COLLECTION'].find({"user": user}).sort(u'_id', -1).count()
    p = app.config['POSTS_COLLECTION'].find({"user": user}).sort(u'_id', -1).limit(per_page).skip(offset)

    pagination = get_pagination(page=page,
                                per_page=per_page,
                                total=count,
                                record_name='posts')
    if user == nickname: 
        if app.config['POSTS_COLLECTION'].find({"user": user}):
            return render_template('user.html',
                               user=user,
                               posts=p,
                               edit=True,
                               User=User(nickname),
                               pagination=pagination)
        else:
            flash("No posts found", category='error')
            return redirect(url_for('posts'))
    elif app.config['POSTS_COLLECTION'].find({"user": nickname}):
            return render_template('user.html',
                               user=user,
                               posts=p,
                               edit=False,
                               User=User(nickname),
                               pagination=pagination)
    elif user == None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('posts'))



@app.route('/edit/<post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    if current_user.get_id() == app.config['POSTS_COLLECTION'].find_one({"_id": ObjectId(post_id) })['user']:

        post_body = app.config['POSTS_COLLECTION'].find_one({"_id": ObjectId(post_id) })['entry']
        post_title = app.config['POSTS_COLLECTION'].find_one({"_id": ObjectId(post_id) })['title']
        post_tags = app.config['POSTS_COLLECTION'].find_one({"_id": ObjectId(post_id) })['tags']
        form = EditForm()
        if request.method == 'POST':
            
            post = form.post.data
            title = form.post_title.data
            tags = form.tags.data.split(',')
            

            try:
                app.config['POSTS_COLLECTION'].update_one({"_id": ObjectId(post_id)}, {"$set":{"entry": post, "title": title, "tags": tags, "updated_on": datetime.datetime.now()}})
                flash("Post Updated", category='success')
                return redirect(url_for('user', nickname=current_user.get_id()))
            except:
                flash("Something went bad....", category='error')
        form.post.data = post_body
        form.post_title.data = post_title
        form.tags.data = post_tags
        return render_template('edit.html', post_id=post_id, form=form)
    else:
         flash("This is not your post...why would you want to edit it????", category='error')
         return redirect(url_for("posts"))


   

    return render_template('edit.html', post=post_body, form=form)



@app.route('/delete/<post_id>')
@login_required
def delete(post_id):
    if current_user.get_id() == app.config['POSTS_COLLECTION'].find_one({"_id": ObjectId(post_id) })['user']:            

        try:
            app.config['POSTS_COLLECTION'].delete_one({"_id": ObjectId(post_id)})
            flash("Post Deleted", category='success')
        except:
            flash("Something went bad....", category='error')
    else:
         flash("This is not your post...why would you want to delete it????", category='error')
         return redirect(url_for("posts"))
    
    return redirect(url_for('user' , nickname=current_user.get_id()))


@app.route('/settings/<user>', methods=['GET', 'POST'])
@login_required
def settings(user):
    if current_user.get_id() == app.config['USERS_COLLECTION'].find_one({"_id": user })['_id'] and app.config['USERS_COLLECTION'].find_one({"_id": user })['confirmed']:
        bio_body = app.config['USERS_COLLECTION'].find_one({"_id": user})['bio']
        form = ProfileForm()
        if request.method == 'POST':
            bio = form.bio.data
            try:
                app.config['USERS_COLLECTION'].update_one({"_id": user}, {"$set":{"bio": bio, "bio_updated_on": datetime.datetime.now()}})
                flash("Bio Updated", category='success')
                return render_template('settings.html', bio=bio, form=form, User=User(user))
            except:
                flash("Something went bad....", category='error')
        form.bio.data = bio_body
        return render_template('settings.html', bio=bio_body, form=form, User=User(user))

    else:
         flash("This is not your page...why would you want to edit it????", category='error')
         return redirect(url_for("posts"))

    return render_template('settings.html', bio=None, form=form)


@lm.user_loader
def load_user(username):
    u = app.config['USERS_COLLECTION'].find_one({"_id": username})
    if not u:
        return None
    return User(u['_id'])




@app.route('/testing')
def port():
    return render_template('port.html')


@app.route('/main')
def main_page():
    print current_user.is_authenticated()
    return render_template('jolla_home.html')

@app.route('/<path:resource>')
def serveStaticResource(resource):
    return send_from_directory('static/', resource)

@app.errorhandler(404)
def page_not_found(e):
    return "Something went wrong"
if __name__ == '__main__':
    app.run()



