#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import ARRAY
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

shows = db.Table('shows',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('start_time', db.DateTime, nullable=False),
    db.Column('venue_id', db.Integer, db.ForeignKey('venues.id')),
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'))
)

class Venue(db.Model):
        __tablename__ = 'venues'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String)
        city = db.Column(db.String(120))
        state = db.Column(db.String(120))
        address = db.Column(db.String(120))
        phone = db.Column(db.String(120))
        image_link = db.Column(db.String(500))
        facebook_link = db.Column(db.String(120))
        website = db.Column(db.String(120))
        genres = db.Column(db.String(500))
        seeking_talent = db.Column(db.Boolean, default=False)
        seeking_description = db.Column(db.String(500))
        artist = db.relationship('Artist', secondary=shows,
            backref=db.backref('venues', lazy=True))

        def __repr__(self):
            return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.artist}>'

        # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
        __tablename__ = 'artists'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String)
        city = db.Column(db.String(120))
        state = db.Column(db.String(120))
        phone = db.Column(db.String(120))
        genres = db.Column(db.String(120))
        image_link = db.Column(db.String(500))
        facebook_link = db.Column(db.String(120))
        website = db.Column(db.String(120))
        seeking_venue = db.Column(db.Boolean)
        seeking_description = db.Column(db.String())

        def __repr__(self):
            return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres}>'

        # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
            format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
            format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#    Venues
#    ----------------------------------------------------------------

@app.route('/venues')
def venues():
    vens = Venue.query.order_by('state').all()
    areas = []
    area = {}
    ven_list = []
    
    ven_city = ''
    ven_state = ''
    n = 0
    for i in range(len(vens)):
        ven = vens[i]
        if i == 0:
            ven_city = ven.city
            ven_state = ven.state
        if ven_city != ven.city:
            area['city'] = ven_city
            area['state'] = ven_state
            area['venues'] = ven_list
            areas.append(area)
            area = {}
            ven_list = []
            n = 0
        if n == 0:
            ven_city = ven.city
            ven_state = ven.state
        ven_dict = {
            'id': ven.id,
            'name': ven.name,
            'num_upcoming_shows': n
        }
        ven_list.append(ven_dict)
        n += 1
    area['city'] = ven_city
    area['state'] = ven_state
    area['venues'] = ven_list
    areas.append(area)
    area = {}
    ven_list = []
        
    
    # TODO: replace with real venues data.
    #             num_shows should be aggregated based on number of upcoming shows per venue.
    
    return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = str(request.form.get('search_term')).lower()
    datas = Venue.query.all()
    data = []

    for ven in datas:
        if search_term in str(ven.name).lower():
            data.append({
                "id": ven.id,
                "name": ven.name,
                "num_upcoming_shows": 0
            })

    response={
        "count": len(data),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    
    ven = Venue.query.get(venue_id)
    shows_ = db.session.execute('SELECT * FROM shows;')
    past_shows = []
    upcoming_shows = []
    ven_shows = [ven_show for ven_show in shows_ if ven_show.venue_id == ven.id]
    for ven_show in ven_shows:
        if dateutil.parser.parse(str(ven_show.start_time)) > datetime.now():
            upcoming_shows.append({
                "artist": ven_show.artist_id,
                "artist": Artist.query.get(ven_show.artist_id).name,
                "artist_image_link": Artist.query.get(ven_show.artist_id).image_link,
                "start_time": str(ven_show.start_time)
            })
        else:
            past_shows.append({
                "artist_id": ven_show.artist_id,
                "artist_name": Artist.query.get(ven_show.artist_id).name,
                "artist_image_link": Artist.query.get(ven_show.artist_id).image_link,
                "start_time": str(ven_show.start_time)
            })
    data = ven.__dict__
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)

#    Create Venue
#    ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    # try:
    req = request.form
    new_venue = Venue(
        name = req.get('name'),
        city = req.get('city'),
        state = req.get('state'),
        address = req.get('address'),
        phone = req.get('phone'),
        image_link = req.get('image_link'),
        facebook_link = req.get('facebook_link')
    )
    print('list', req.getlist('genres'))
    genres = f'[{", ".join(req.getlist("genres"))}]'
    print('genres', type(genres), genres)
    # print(new_venue)
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#    Artists
#    ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    
    data = Artist.query.order_by('id').all()
    
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = str(request.form.get('search_term')).lower()
    datas = Artist.query.all()
    data = []

    for art in datas:
        if search_term in str(art.name).lower():
            data.append({
                "id": art.id,
                "name": art.name,
                "num_upcoming_shows": 0
            })

    response={
        "count": len(data),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    import ast
    art = Artist.query.get(artist_id)
    art.genres = ast.literal_eval(art.genres)
    shows_ = db.session.execute('SELECT * FROM shows;')
    # data = []
    
    past_shows = []
    upcoming_shows = []
    art_shows = [art_show for art_show in shows_ if art_show.artist_id == art.id]
    for art_show in art_shows:
        if dateutil.parser.parse(str(art_show.start_time)) > datetime.now():
            upcoming_shows.append({
                "venue_id": art_show.venue_id,
                "venue_name": Venue.query.get(art_show.venue_id).name,
                "venue_image_link": Venue.query.get(art_show.venue_id).image_link,
                "start_time": str(art_show.start_time)
            })
        else:
            past_shows.append({
                "venue_id": art_show.venue_id,
                "venue_name": Venue.query.get(art_show.venue_id).name,
                "venue_image_link": Venue.query.get(art_show.venue_id).image_link,
                "start_time": str(art_show.start_time)
            })
    data = art.__dict__
    data['past_shows'] = past_shows
    data['upcoming_shows'] = upcoming_shows
    data['past_shows_count'] = len(past_shows)
    data['upcoming_shows_count'] = len(upcoming_shows)
    # genres = genres.split('\"')
    # i = 0
    # while len(genres) <= i:
    #     if genres[i] in ['\"', '[', ']', '', '']:
    #         del genres[i]
    #     i += 1
    
    return render_template('pages/show_artist.html', artist=data)

#    Update
#    ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist={
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue={
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))

#    Create Artist
#    ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#    Shows
#    ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #             num_shows should be aggregated based on number of upcoming shows per venue.
    
    shows_ = db.session.execute('SELECT * FROM shows;')

    # shows_ = db.session.query(shows).all()
    data = []

    for show in shows_:
        ven = Venue.query.get(show.venue_id)
        art = Artist.query.get(show.artist_id)
        data_dict = {
            "venue_id": show.venue_id,
            "venue_name": ven.name,
            "artist_id": show.artist_id,
            "artist_name": art.name,
            "artist_image_link": art.image_link,
            "start_time": str(show.start_time)
        }
        data.append(data_dict)

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
        return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
        return render_template('errors/500.html'), 500


if not app.debug:
        file_handler = FileHandler('error.log')
        file_handler.setFormatter(
                Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        )
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
        app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
'''
