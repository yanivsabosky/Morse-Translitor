from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from func import display_in_morse_way
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///Morse.db')
Bootstrap5(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CONFIGURE TABLE
class BlogMorsePost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    word: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    translated_word: Mapped[str] = mapped_column(String(250), nullable=False)

# Initialize Database
with app.app_context():
    db.create_all()

# Form Class
class NMorse(FlaskForm):
    word = StringField('Your Word To Translate', validators=[DataRequired()])
    sub = SubmitField('Submit Word')

# Define Routes
@app.route('/')
def get_all_posts():
    posts = db.session.execute(db.select(BlogMorsePost)).scalars().all()
    return render_template("index.html", all_posts=posts)

@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = db.get_or_404(BlogMorsePost, post_id)
    return render_template('post.html', post=requested_post)

@app.route('/new-post', methods=['GET', 'POST'])
def create_post():
    form = NMorse()
    if form.validate_on_submit():
        nPost = BlogMorsePost(
            word=form.word.data,
            translated_word=display_in_morse_way(form.word.data)  # Auto-generate Morse translation
        )
        db.session.add(nPost)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)

@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def ed_post(post_id):
    post = db.get_or_404(BlogMorsePost, post_id)
    edit_form = NMorse(word=post.word)
    if edit_form.validate_on_submit():
        post.word = edit_form.word.data
        post.translated_word = display_in_morse_way(edit_form.word.data)
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)

@app.route('/delete/<int:post_id>')
def delete(post_id):
    post = db.get_or_404(BlogMorsePost, post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact', methods=["GET", "POST"])
def contact():
    return render_template("contact.html")

# Inject Current Year for Footer
@app.context_processor
def inject_year():
    from datetime import datetime
    return {'current_year': datetime.now().year}

if __name__ == "__main__":
    app.run(port=5000)  # Removed debug=True for security
