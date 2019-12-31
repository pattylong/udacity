#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json

import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pattylong:hello@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
migrate = Migrate(app, db)
moment = Moment(app)


from models import *


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


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  time_now = datetime.now()
  locations = db.session.query(Venue.city, Venue.state).distinct()
  for loc in locations:
    data.append({
      "city": loc.city,
      "state": loc.state,
      "venues": []
    })
    venues_at_loc = db.session.query(Venue).filter_by(city=loc.city, state=loc.state).all()

    for venue in venues_at_loc:
      upcoming_shows_count = venue.shows.filter(time_now <= Show.start_time).count()
      data[len(data)-1]["venues"].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": upcoming_shows_count
      })

  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '').lower()
  search_term_adj = '%{0}%'.format(search_term)
  venues_like_search = db.session.query(Venue).filter(Venue.name.ilike(search_term_adj)).all()
  data = []
  for venue in venues_like_search:
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": venue.shows.count()
    })

  response = {
    "count": len(venues_like_search),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  time_now = datetime.now()
  venue = db.session.query(Venue).filter_by(id=venue_id).first()

  past_shows = venue.shows.filter(time_now > Show.start_time).all()
  past_shows_count = len(past_shows)
  upcoming_shows = venue.shows.filter(time_now <= Show.start_time).all()
  upcoming_shows_count = len(upcoming_shows)

  past_shows_data = []
  for show in past_shows:
    artist = db.session.query(Artist).filter_by(id=show.artist_id).first()
    past_shows_data.append({
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    })

  upcoming_shows_data = []
  for show in upcoming_shows:
    artist = db.session.query(Artist).filter_by(id=show.artist_id).first()
    upcoming_shows_data.append({
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    })

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows_data,
    "upcoming_shows": upcoming_shows_data,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    error = False
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    seeking_talent = request.form['seeking_talent'] == 'y'
    seeking_description = request.form['seeking_description']

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres,
                  facebook_link=facebook_link, image_link=image_link, seeking_talent=seeking_talent,
                  seeking_description=seeking_description)

    db.session.add(venue)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET', 'DELETE'])
def delete_venue(venue_id):
  try:
    error = False
    venue = db.session.query(Venue).get(venue_id)
    db.session.delete(venue)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  if not error:
    flash('Venue was successfully deleted.')

  else:
    flash('An error occurred. Venue could not be deleted.')

  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  all_artists = db.session.query(Artist).all()
  data = []
  for artist in all_artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  time_now = datetime.now()
  artist = db.session.query(Artist).filter_by(id=artist_id).first()

  past_shows = artist.shows.filter(time_now > Show.start_time).all()
  past_shows_count = len(past_shows)
  past_shows_data = []
  for show in past_shows:
    venue = db.session.query(Venue).filter_by(id=show.venue_id).first()
    past_shows_data.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    })

  upcoming_shows = artist.shows.filter(time_now <= Show.start_time).all()
  upcoming_shows_count = len(upcoming_shows)
  upcoming_shows_data = []
  for show in upcoming_shows:
    venue = db.session.query(Venue).filter_by(id=show.venue_id).first()
    upcoming_shows_data.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    })

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "website": artist.website,
    "image_link": artist.image_link,
    "past_shows": past_shows_data,
    "upcoming_shows": upcoming_shows_data,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }

  return render_template('pages/show_artist.html', artist=data)

@app.route('/artists/<artist_id>/delete', methods=['GET', 'DELETE'])
def delete_artist(artist_id):
  try:
    error = False
    artist = db.session.query(Artist).get(artist_id)
    db.session.delete(artist)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  if not error:
    flash('Artist was successfully deleted.')

  else:
    flash('An error occurred. Artist could not be deleted.')

  return render_template('pages/home.html')

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  if request.method == 'GET':
    form = ArtistForm()

    artist = db.session.query(Artist).get(artist_id)
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link

    artist = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link
    }

    return render_template('forms/edit_artist.html', form=form, artist=artist)

  else:
    return redirect(url_for('edit_artist_submission', artist_id=artist_id))


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  if request.method == 'POST':
    try:
      error = False
      artist = db.session.query(Artist).get(artist_id)
      artist.name = request.form['name']
      artist.city = request.form['city']
      artist.state = request.form['state']
      artist.phone = request.form['phone']
      artist.genres = request.form.getlist('genres')
      artist.facebook_link = request.form['facebook_link']
      artist.image_link = request.form['image_link']
      artist.website = request.form['website']
      print("is it this")
      seek_venue = request.form['seeking_venue'] == 'y'
      print("so dumb ugh")
      artist.seeking_venue = seek_venue
      artist.seeking_description = request.form['seeking_description']
      db.session.commit()

    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())

    finally:
      db.session.close()

    if not error:
      flash('Artist ' + request.form['name'] + ' was successfully edited!')

    else:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')

    return redirect(url_for('show_artist', artist_id=artist_id))

  else:
    return redirect(url_for('edit_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  if request.method == 'GET':
    form = VenueForm()

    venue = db.session.query(Venue).get(venue_id)
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.website.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link

    venue = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link
    }

    return render_template('forms/edit_venue.html', form=form, venue=venue)

  else:
    return redirect(url_for('edit_venue_submission', venue_id=venue_id))


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  if request.method == 'POST':
    try:
      error = False
      venue = db.session.query(Venue).get(venue_id)
      venue.name = request.form['name']
      venue.city = request.form['city']
      venue.state = request.form['state']
      venue.address = request.form['address']
      venue.phone = request.form['phone']
      venue.genres = request.form.getlist('genres')
      venue.facebook_link = request.form['facebook_link']
      venue.image_link = request.form['image_link']
      venue.website = request.form['website']
      seek_talent = request.form['seeking_talent'] == 'y'
      venue.seeking_talent = seek_talent
      venue.seeking_description = request.form['seeking_description']
      print("the eff")
      db.session.commit()

    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())

    finally:
      db.session.close()

    if not error:
      flash('Venue ' + request.form['name'] + ' was successfully edited!')

    else:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')

    return redirect(url_for('show_venue', venue_id=venue_id))

  else:
    return redirect(url_for('edit_venue', venue_id=venue_id))



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    error = False
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    seeking_venue = request.form['seeking_venue'] == 'y'
    seeking_description = request.form['seeking_description']

    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres,
                    facebook_link=facebook_link, image_link=image_link, seeking_venue=seeking_venue,
                    seeking_description=seeking_description)

    db.session.add(artist)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  time_now = datetime.now()
  upcoming_shows = db.session.query(Show).filter(time_now <= Show.start_time).all()
  data = []

  for show in upcoming_shows:
    venue = db.session.query(Venue).filter_by(id=show.venue_id).first()
    artist = db.session.query(Artist).filter_by(id=show.artist_id).first()
    data.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    })

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
  try:
    error = False
    error_msg = ""

    time_now = datetime.now()
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    venue_exists = db.session.query(Venue.id).filter_by(id=venue_id).scalar() is not None
    artist_exists = db.session.query(Artist.id).filter_by(id=artist_id).scalar() is not None
    valid_time = time_now < dateutil.parser.parse(start_time)

    if not venue_exists:
      error_msg = 'Venue id is not valid.'
      raise ValueError('Venue id is not valid.')
    if not artist_exists:
      error_msg = 'Artist id is not valid.'
      raise ValueError('Artist id is not valid.')
    if not valid_time:
      error_msg = 'Show time must be in the future.'
      raise ValueError('Show time must be in the future.')

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    if not error_msg:
      error_msg = 'An error occurred. Show could not be listed.'

  finally:
    db.session.close()

  if not error:
    flash('Show was successfully listed!')
  else:
    flash(error_msg)
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
