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
from sqlalchemy.orm import aliased
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
db.init_app(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:Nada1415@localhost:5432/fyyurdb'

Migrate = Migrate(app,db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.Text)
    seeking_talent = db.Column(db.Boolean, default=False)
    upcoming_shows = db.relationship("Show", backref='some_venue')
    def __repr__(self):
      return f'<Venue {self.id}, Venue name:{self.name}>'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.Text)
    upcoming_shows = db.relationship("Show", backref='some_artist')
    def __repr__(self):
      return f'<Artist {self.id}, Artist name:{self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True) 
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  start_time = db.Column(db.String(17), nullable=False)
  def __repr__(self):
    return f'<Artist ID: {self.artist_id}, Venue ID:{self.venue_id}>'

   # db.create_all()

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  now = datetime.datetime.now()
  venues = db.session.query(Venue.id,Venue.city, Venue.state, Venue.name,Venue.upcoming_shows).group_by(Venue.id,Venue.city, Venue.state, Venue.name,Venue.upcoming_shows).all()

  CityAndState =''
  data = []
  for v in venues:
    if CityAndState != v.city + v.state:
      data.append({
      "city": v[1],
      "state": v[2],
      "venues": []
      })
      CityAndState = v.city + v.state

      if CityAndState == v.city + v.state:
        data[len(data) -1]["venues"].append({
          "id": v[0],
          "name": v[3],
          "num_upcoming_shows": v[4]

          })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  venues = Venue.query.filter(func.lower(Venue.name).contains(func.lower(request.form.get('search_term')))).all()
  response = {
    "count": len(venues),
    "data": []}
  for v in venues:
    response["data"].append({
      "id": v.id,
      "name": v.name,
      "num_upcoming_shows": len(v.upcoming_shows)
      })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):


  venues = db.session.query(Venue).filter_by(id = venue_id).first()
  shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).all()
  current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  past_shows = []
  coming_shows = []
  new_genres =[]
  new_genre=''
  
  for show in shows:
    if (show.start_time < current_time):
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.some_artist.name,
        "artist_image_link": show.some_artist.image_link,
        "start_time": show.start_time
        })
    else:
      coming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.some_artist.name,
      "artist_image_link": show.some_artist.image_link,
      "start_time": show.start_time  
    })

  for genre in venues.genres:
    if (genre is not '{' and genre is not ','):
      new_genre=new_genre+genre
    if genre == ",":
      new_genres.append(new_genre)
      new_genre=''

  data={
    "id": venues.id,
    "name": venues.name,
    "genres": new_genres,
    "address": venues.address,
    "city": venues.city,
    "state": venues.state,
    "phone": venues.phone,
    "website": venues.website,
    "facebook_link": venues.facebook_link,
    "seeking_talent": venues.seeking_talent,
    "seeking_description": venues.seeking_description,
    "image_link": venues.image_link,
    "past_shows":past_shows,
    "upcoming_shows": coming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(coming_shows),
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
    venue = Venue(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      address = request.form.get('address'),
      phone = request.form.get('phone'),
      genres = request.form.getlist('genres'),
      image_link = request.form.get('image_link'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website'),
      seeking_description = request.form.get('seeking_description'),
      seeking_talent = True if 'seeking_talent' in request.form else False ,
    )
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
      db.session.rollback()
      flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    
  finally:
       db.session.close()
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage 

  try:
    db.session.query(Venue).filter_by(id = venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback() 
  finally:
    db.session.close()

  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists = db.session.query(Artist).group_by(Artist.id, Artist.name).all()

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  artist= Artist.query.filter(func.lower(Artist.name).contains(func.lower(request.form.get('search_term')))).all()
  response = {
    "count": len(artist),
    "data": []}
  for a in artist:
    response["data"].append({
      "id": a.id,
      "name": a.name,
      "num_upcoming_shows": a.upcoming_shows
      })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = db.session.query(Artist).filter_by(id = artist_id).first()
  shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).all()
  current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  past_shows = []
  coming_shows = []
  new_genres =[]
  new_genre=''

  
  for show in shows:
    if (show.start_time < current_time):
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.some_artist.name,
        "artist_image_link": show.some_artist.image_link,
        "start_time": show.start_time
        })
    else:
      coming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.some_artist.name,
      "artist_image_link": show.some_artist.image_link,
      "start_time": show.start_time  
    })

  
  for genre in artist.genres:
    if (genre is not '{' and genre is not ','):
      new_genre=new_genre+genre
    if genre == ",":
      new_genres.append(new_genre)
      new_genre=''



  data={
    "id": artist.id,
    "name":artist.name ,
    "genres": new_genres,
    "city": artist.city,
    "state":artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": coming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(coming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artst = db.session.query(Artist).filter_by(id = artist_id).first()
  form.name.data = artst.name
  form.genres.data = artst.genres
  form.city.data = artst.city
  form.state.data = artst.state
  form.phone.data = artst.phone
  form.image_link.data = artst.image_link
  form.facebook_link.data = artst.facebook_link
  form.website.data = artst.website
  form.seeking_venue.data = artst.seeking_venue
  form.seeking_description.data = artst.seeking_description
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artst)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attribute
  artist = Artist.query.get(artist_id)
  try:
      artist.name = request.form.get('name')
      artist.city = request.form.get('city')
      artist.state = request.form.get('state')
      artist.phone = request.form.get('phone')
      artist.genres = request.form.getlist('genres')
      artist.image_link = request.form.get('image_link')
      artist.facebook_link = request.form.get('facebook_link')
      artist.website = request.form.get('website')
      artist.seeking_venue = True if 'seeking_venue' in request.form else False 
      artist.seeking_description = request.form.get('seeking_description')
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully edited!')
  except:
      db.session.rollback()
  finally:
       db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
 
  # TODO: populate form with values from venue with ID <venue_id>
  venue = db.session.query(Venue).filter_by(id = venue_id).first()
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.website.data = venue.website
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  venue = Venue.query.get(venue_id)
  try:
      venue.name = request.form.get('name')
      venue.city = request.form.get('city')
      venue.state = request.form.get('state')
      venue.phone = request.form.get('phone')
      venue.genres = request.form.getlist('genres')
      venue.image_link = request.form.get('image_link')
      venue.facebook_link = request.form.get('facebook_link')
      venue.website = request.form.get('website')
      venue.seeking_talent = True if 'seeking_venue' in request.form else False 
      venue.seeking_description = request.form.get('seeking_description')
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully edited!')
  except:
      db.session.rollback()
  finally:
       db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()

  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    artist = Artist(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),
      genres = request.form.getlist('genres'),
      image_link = request.form.get('image_link'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website'),
      seeking_venue = True if 'seeking_venue' in request.form else False ,
      seeking_description = request.form.get('seeking_description'),
    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + 'could not be listed. ')
    
  finally:
       db.session.close()
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.


  shows = db.session.query(Show).join(Artist).join(Venue).all()

  shows_data = []
  for s in shows:
    shows_data.append({
      "venue_id": s.venue_id ,
      "venue_name": s.some_venue.name,
      "artist_id": s.some_artist.id,
      "artist_name": s.some_artist.name, 
      "artist_image_link": s.some_artist.image_link,
      "start_time": s.start_time
    })




  return render_template('pages/shows.html', shows=shows_data)

@app.route('/shows/create')
def create_shows():

  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    show = Show(
      artist_id = request.form.get('artist_id'),
      venue_id = request.form.get('venue_id'),
      start_time = request.form.get('start_time'),
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  except:
      db.session.rollback()
      flash('An error occurred. The Show could not be listed. ')
    
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
