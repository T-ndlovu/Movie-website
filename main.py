from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import requests

api_key = "3c66cca85cdf70126341eb2104739595"
api_token = ("eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzYzY2Y2NhODVjZGY3MDEyNjM0MWViMjEwNDczOTU5NSIsInN1YiI6IjY1YTU0NmExOGRi"
             "YzMzMDEyOTZhN2NmNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.G-5T9PemKHwmbiUY6YvrkcHM4e-e9M88-"
             "VRBFbSX6ok")

db = SQLAlchemy()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_collection.db'
db.init_app(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    year = db.Column(db.Integer)
    description = db.Column(db.String)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String)
    img_url = db.Column(db.String)


# with app.app_context():
#     db.create_all()
#
# with app.app_context():
#     new_book = Movie(title="Phone Book", year=2002, description="Publicist Stuart Shepard finds himself trapped "
#                                                                 "in a phone booth, pinned down "
#                              "by an extortionist's sniper rifle. Unable to leave or receive outside help, "
#                              "Stuart's negotiation with the caller leads to a jaw-dropping climax.", rating=7.3,
#                      ranking=10, review="My favourite character was the caller.",
#                      img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg")
#     new_book = Movie(title="Avatar The Way of Water", year=2022, description="Set more than a decade after the events"
#                  "of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the "
#                  "trouble that follows them, the lengths they go to keep each other safe, the battles they fight to "
#                  "stay alive, and the tragedies they endure.",
#                      rating=7.3,
#                      ranking=9, review="I liked the water.",
#                      img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg")
#     db.session.add(new_book)
#     db.session.commit()
class RateMovie(FlaskForm):
    rating = StringField('Your rating out of 10 eg. 6.5')
    review = StringField('Your review')
    submit = SubmitField('Done')


class AddMovie(FlaskForm):
    name = StringField('Movie Title')
    submit = SubmitField('Add Movie')


@app.route("/")
def home():
    data = db.session.execute(db.select(Movie).order_by(Movie.rating)).scalars()
    all_movies = data.all()
    for n in range(len(all_movies)):
        all_movies[n].ranking = len(all_movies) - n
        db.session.commit()
    return render_template("index.html", data=all_movies)


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    form = RateMovie()
    movie_id = request.args.get('id')
    content = db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        content.rating = float(form.rating.data)
        content.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html', movie=content, form=form)


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie_deleted = db.get_or_404(Movie, movie_id)
    db.session.delete(movie_deleted)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddMovie()

    if form.validate_on_submit():
        title = form.name.data
        url = f"https://api.themoviedb.org/3/search/movie?query={title}&include_adult=false&language=en-US&page=1"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
        response = requests.get(url, headers=headers).json()['results']
        return render_template('select.html', data=response)

    return render_template('add.html', form=form)


@app.route('/select')
def select():
    search_id = request.args.get('id')
    url = f"https://api.themoviedb.org/3/movie/{search_id}?language=en-US"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    res = requests.get(url, headers=headers).json()
    title = res['original_title']
    des = res['overview']
    release = res['release_date']
    img_url = res['poster_path']
    with app.app_context():
        new_movie = Movie(title=title, year=release, description=des, img_url=f'https://image.tmdb.org/t/p/w500/{img_url}')
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit", id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
