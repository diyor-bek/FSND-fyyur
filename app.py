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
import ast
import sys
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
    vens = Venue.query.order_by('city').all()
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
    shows_ = db.session.execute('SELECT * FROM shows;')

    for ven in datas:
        if search_term in str(ven.name).lower():
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
            data.append({
                'id': ven.id,
                'name': ven.name,
                'genres': ast.literal_eval(ven.genres),
                'past_shows': past_shows,
                'upcoming_shows': upcoming_shows,
                'past_shows_count': len(past_shows),
                'upcoming_shows_count': len(upcoming_shows)
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
    data['genres'] = ast.literal_eval(ven.genres)
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
    try:
        req = request.form
        new_venue = Venue(
            name = req.get('name'),
            city = req.get('city'),
            state = req.get('state'),
            address = req.get('address'),
            phone = req.get('phone'),
            image_link = req.get('image_link'),
            facebook_link = req.get('facebook_link', ''),
            genres = '[\"' + '\", \"'.join(req.getlist("genres")) + '\"]',
            website = req.get('website_link', ''),
            seeking_talent = req.get('seeking_description', '')!='',
            seeking_description = req.get('seeking_description')
        )
        db.session.add(new_venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.', 'error')
    finally:
        db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    body = {}
    try:
        ven = Venue.query.get(venue_id)
        db.session.execute('DELETE FROM shows WHERE venue_id = ' + str(venue_id))
        db.session.delete(ven)
        db.session.commit()
        body['success'] = True
    except Exception as e:
        db.session.rollback()
        print(sys.exc_info(), '\n\n')
        print(e)
        body['success'] = False
    finally:
        db.session.close()
    return body

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
    shows_ = db.session.execute('SELECT * FROM shows;')

    for art in datas:
        if search_term in str(art.name).lower():
            art.genres = ast.literal_eval(art.genres)
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
            data.append({
                "id": art.id,
                "name": art.name,
                'past_shows': past_shows,
                'upcoming_shows': upcoming_shows,
                'past_shows_count': len(past_shows),
                'upcoming_shows_count': len(upcoming_shows)
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

    return render_template('pages/show_artist.html', artist=data)

#    Update
#    ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    req = request.form
    art = Artist.query.get(artist_id)
    art.name = req.get('name')
    art.city = req.get('city')
    art.state = req.get('state')
    art.genres = '[\"' + '\", \"'.join(req.getlist('genres')) + '\"]'
    art.facebook_link = req.get('facebook_link')
    art.website = req.get('website')
    art.image_link = req.get('image_link')
    art.seeking_venue = req.get('seeking_description')!=''
    art.seeking_description = req.get('seeking_description')
    db.session.commit()
    db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    req = request.form
    venue = Venue.query.get(venue_id)
    venue.name = req.get('name')
    venue.city = req.get('city')
    venue.state = req.get('state')
    venue.address = req.get('address')
    venue.phone = req.get('phone')
    venue.genres = '[\"' + '\", \"'.join(req.getlist('genres')) + '\"]'
    venue.facebook_link = req.get('facebook_link')
    venue.website = req.get('website_link')
    venue.image_link = req.get('image_link')
    venue.seeking_venue = req.get('seeking_description')!=''
    venue.seeking_description = req.get('seeking_description')
    db.session.commit()
    db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#    Create Artist
#    ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        new_artist = Artist(
            name = request.form.get('name'),
            city = request.form.get('city'),
            state = request.form.get('state'),
            phone = request.form.get('phone'),
            image_link = request.form.get('image_link'),
            facebook_link = request.form.get('facebook_link'),
            seeking_venue = request.form.get('seeking_description')!='',
            seeking_description = request.form.get('seeking_description'),
            website = request.form.get('website'),
            genres = '[\"' + '\", \"'.join(list(request.form.getlist('genres'))) + '"]'
        )
        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + request.form.get('name') + ' was successfully listed!')
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


#    Shows
#    ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows_ = db.session.execute('SELECT * FROM shows;')
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
    try:
        ven = request.form.get('venue_id')
        art = request.form.get('artist_id')
        s_t = str(request.form.get('start_time'))
        db.session.execute(f'INSERT INTO shows (artist_id, venue_id, start_time) VALUES ({art}, {ven}, \'{s_t}\');')
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
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
