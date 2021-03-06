# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, URL
from flask.ext.wtf.recaptcha import RecaptchaField
from flask.ext.pagedown.fields import PageDownField


class LoginForm(Form):
    """Login form to access writing and settings pages"""

    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})

class SignupForm(Form):
    username_signup = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Username"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "email"})
    password_signup = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    recap = RecaptchaField()

class PostForm(Form):
    post = PageDownField('Markdown supported', render_kw={"placeholder": "..."})
    pagedown = PageDownField()
    post_title = StringField(render_kw={"placeholder": "TITLE"})
    tags = StringField()

class EditForm(Form):
    post = PageDownField('Markdown supported')
    pagedown = PageDownField()
    post_title = StringField(validators=[DataRequired()], render_kw={"placeholder": "Title"})
    tags = StringField()
    

class ProfileForm(Form):
    bio = TextAreaField('bio')

class Comments(Form):
    comment = TextAreaField(render_kw={"placeholder": "Comment here"})

class QuickPost(Form):
    link = StringField(validators=[DataRequired(), URL()], render_kw={"placeholder": "link, youtube, imgur, twitter, xkcd", "style": "display:none"})
    random = StringField(validators=[DataRequired()], render_kw={"placeholder": "thoughts, jokes, questions....", "style": "display:none"})
