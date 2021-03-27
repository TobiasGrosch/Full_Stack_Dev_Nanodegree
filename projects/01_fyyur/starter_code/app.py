#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app, session_options={"expire_on_commit": False})

migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    upcoming_shows = db.relationship('Show', backref='venue_upcoming', lazy=True)
    past_shows = db.relationship('Show', backref='venue_past', lazy=True)
    upcoming_shows_count = db.Column(db.Integer)
    past_shows_count = db.Column(db.Integer)
    

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    upcoming_shows = db.relationship('Show', backref='artist_upcoming', lazy=True)
    past_shows = db.relationship('Show', backref='artist_past', lazy=True)
    upcoming_shows_count = db.Column(db.Integer)
    past_shows_count = db.Column(db.Integer)


class Show(db.Model):
    __tablename__='Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  locals = []
  venues = Venue.query.all()
  places = Venue.query.distinct(Venue.city, Venue.state).all()
	
  for place in places:
    locals.append({
        'city': place.city,
        'state': place.state,
        'venues': [{
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len([show for show in venue.upcoming_shows if show.start_time > datetime.now()])
        } for venue in venues if
            venue.city == place.city and venue.state == place.state]
    })
  return render_template('pages/venues.html', areas=locals)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form['search_term']
  response = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()
  response={"data": response}

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)

  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    ).all()

  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
    ).all()

  data = {
        'id': venue.id,
        'name': venue.name,
        'city': venue.city,
        'state': venue.state,
        'address': venue.address,
        'phone': venue.phone,
        'genres': venue.genres,
        'facebook_link': venue.facebook_link,
        'website_link': venue.website_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': [{
            'artist_id': artist.id,
            'artist_image_link': artist.image_link,
            'artist_name': artist.name,
            'start_time': str(show.start_time)
        } for artist, show in past_shows],
        'upcoming_shows': [{
            'artist_id': artist.id,
            'artist_image_link': artist.image_link,
            'artist_name': artist.name,
            'start_time': str(show.start_time)
        } for artist, show in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()

  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  name =  request.form['name']
  genres = request.form['genres']
  address = request.form['address']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  website_link = request.form['website_link']
  facebook_link = request.form['facebook_link']
  try:
    seeking_talent = request.form['seeking_talent']
  except:
    seeking_talent = False
  image_link = request.form['image_link']
  if seeking_talent == 'y':
    seeking_talent = True
    seeking_description = request.form['seeking_description']
    venue = Venue(name=name, genres=genres, address=address, city=city, state=state, phone=phone, website_link=website_link, 
    facebook_link=facebook_link, image_link=image_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
  else:
    venue = Venue(name=name, genres=genres, address=address, city=city, state=state, phone=phone, website_link=website_link, 
    facebook_link=facebook_link, image_link=image_link, seeking_talent=seeking_talent, seeking_description=None)
  try:
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    abort(500)
  else: 
    return jsonify({ 'success': True })
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form['search_term']
  response = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()
  response={"data": response}

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)

  past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
        Show.venue_id == Venue.id,
        Show.artist_id == artist.id,
        Show.start_time < datetime.now()
    ).all()

  upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
        Show.venue_id == Venue.id,
        Show.artist_id == artist.id,
        Show.start_time > datetime.now()
    ).all()

  data = {
        'id': artist.id,
        'name': artist.name,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'genres': artist.genres,
        'facebook_link': artist.facebook_link,
        'website_link': artist.website_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,
        'past_shows': [{
            'venue_id': venue.id,
            'venue_image_link': venue.image_link,
            'venue_name': venue.name,
            'start_time': str(show.start_time)
        } for venue, show in past_shows],
        'upcoming_shows': [{
            'venue_id': venue.id,
            'venue_image_link': venue.image_link,
            'venue_name': venue.name,
            'start_time': str(show.start_time)
        } for venue, show in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  name =  request.form['name']
  genres = request.form['genres']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  website_link = request.form['website_link']
  facebook_link = request.form['facebook_link']
  try:
    seeking_venue = request.form['seeking_venue']
  except:
    seeking_venue = False
  image_link = request.form['image_link']
  if seeking_venue == 'y':
    seeking_venue = True
    seeking_description = request.form['seeking_description']
  else:
    seeking_talen = False
    seeking_description = None
  try:
    a = db.session.query(Artist).get(artist_id)
    a.name = name
    a.genres = genres
    a.city = city
    a.state = state
    a.phone = phone
    a.website_link = website_link
    a.facebook_link = facebook_link
    a.seeking_venue = seeking_venue
    a.seeking_description = seeking_description
    a.image_link = image_link
    db.session.commit()
    flash('Artist ' + name + ' was successfully updated!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + name + ' could not be updated.')
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  name =  request.form['name']
  genres = request.form['genres']
  city = request.form['city']
  state = request.form['state']
  adress = request.form['address']
  phone = request.form['phone']
  website_link = request.form['website_link']
  facebook_link = request.form['facebook_link']
  try:
    seeking_talent = request.form['seeking_talent']
  except:
    seeking_talent = False
  image_link = request.form['image_link']
  if seeking_talent == 'y':
    seeking_talent = True
    seeking_description = request.form['seeking_description']
  else:
    seeking_talent = False
    seeking_description = None
  try:
    v = db.session.query(Venue).get(venue_id)
    v.name = name
    v.genres = genres
    v.city = city
    v.state = state
    v.phone = phone
    v.website_link = website_link
    v.facebook_link = facebook_link
    v.seeking_talent = seeking_talent
    v.seeking_description = seeking_description
    v.image_link = image_link
    db.session.commit()
    flash('Venue ' + name + ' was successfully updated!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + name + ' could not be updated.')
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  name =  request.form['name']
  genres = request.form['genres']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  website_link = request.form['website_link']
  facebook_link = request.form['facebook_link']
  try:
    seeking_venue = request.form['seeking_venue']
  except:
    seeking_venue = False
  image_link = request.form['image_link']
  if seeking_venue == 'y':
    seeking_venue = True
    seeking_description = request.form['seeking_description']
    artist = Artist(name=name, genres=genres, city=city, state=state, phone=phone, website_link=website_link, 
    facebook_link=facebook_link, image_link=image_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
  else:
    artist = Artist(name=name, genres=genres, city=city, state=state, phone=phone, website_link=website_link, 
    facebook_link=facebook_link, image_link=image_link, seeking_venue=seeking_venue, seeking_description=None)
  try:
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.order_by(Show.start_time.desc()).all()
  data = []
  for show in shows:
    venue = Venue.query.filter_by(id=show.venue_id).first()
    artist = Artist.query.filter_by(id=show.artist_id).first()
    data.append({
      "venue_id": venue.id,
      "venue_name": venue.name,       
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time),
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  artist_id =  request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']
  show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
  try:
    db.session.add(show)
    db.session.commit()
    flash('Show at ' + start_time + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show at ' + start_time + ' could not be listed.')
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
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
