#!/usr/bin/env python2.7

"""Create web views for the Wine App"""

from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   jsonify,
                   url_for,
                   make_response,
                   session as login_session)
from sqlalchemy import (create_engine,
                        asc)
from sqlalchemy.orm import sessionmaker
from models import (Base,
                    Country,
                    Wine,
                    User)
import random
import string
from oauth2client.client import (flow_from_clientsecrets,
                                 FlowExchangeError)
import httplib2
import json
import requests
from functools import wraps

GOOGLE_CLIENT_ID = json.loads(open(
    'client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine(
    'sqlite:///wines.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


@app.route('/login')
def showLogin():
    """At login, create a state token to prevent request forgery"""
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template(
        'login.html', state=state, GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Log in with Facebook"""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?'
    url += 'grant_type=fb_exchange_token&client_id=%s'
    url += '&client_secret=%s&fb_exchange_token=%s'
    realurl = url % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(realurl, 'GET')[1]
    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    token = result.split(',')[0].split(':')[1].replace('"', '')
    url = 'https://graph.facebook.com/v2.8/me?access_token=%s'
    url += '&fields=name,id,email'
    realurl = url % token
    h = httplib2.Http()
    result = h.request(realurl, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data.get('name', '')
    login_session['email'] = data.get('email', '')
    login_session['facebook_id'] = data.get('id', '')

    # The token must be stored in the login_session in order to logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s'
    url += '&redirect=0&height=200&width=200'
    realurl = url % token
    h = httplib2.Http()
    result = h.request(realurl, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data["data"]["url"]

    # See if user exists in wine.db
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Redirect to success page (NOT WORKING)
    return render_template('loginsuccess.html', ls=login_session)


@app.route('/fbdisconnect')
def fbdisconnect():
    """Log out specific to Facebook"""
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?'
    url += 'access_token=%s'
    realurl = url % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Log in with Google"""
    if request.args.get('state') != login_session['state']:
        print 'INVALID STATE'
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        print 'FAILED TO UPGRADE'
        response = make_response(json.dumps(
            'Failed to upgrade the authorization code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid
    access_token = credentials.access_token
    login_session['access_token'] = access_token
    url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?'
    url += 'access_token=%s'
    realurl = url % access_token
    h = httplib2.Http()
    result = json.loads(h.request(realurl, 'GET')[1])
    # If there was an error in the access token info, abort
    if result.get('error') is not None:
        print 'USER ID MISMATCH'
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user id"), 401)
        response.headers['Content-Type'] = 'application.json'
        return response
    # Verify that the access token is valid for this app
    if result['issued_to'] != GOOGLE_CLIENT_ID:
        print 'CLIENT ID MISMATCH'
        response = make_response(json.dumps(
            "Token's client id does not match app's"), 401)
        response.headers['Content-Type'] = 'application.json'
        return response
    # Check to see if user is already logged in
    google_id = credentials.id_token['sub']
    stored_credentials = login_session.get('credentials')
    stored_google_id = login_session.get('google_id')
    if stored_credentials is not None and google_id == stored_google_id:
        print 'ALREADY CONNECTED'
        response = make_response(json.dumps(
            'Current user is already connected'), 200)
        response.headers['Content-Type'] = 'application.json'
    # Store the access token in the session for later use
    login_session['provider'] = 'google'
    # login_session['credentials'] = credentials
    login_session['google_id'] = google_id
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    login_session['username'] = data.get('name', '')
    login_session['picture'] = data.get('picture', '')
    login_session['email'] = data.get('email', '')
    # See if user exists in wine.db
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    return render_template('loginsuccess.html', ls=login_session)


@app.route('/gdisconnect')
def gdisconnect():
    """Log out specific to Google"""
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?'
    url += 'token=%s'
    realurl = url % login_session['access_token']
    h = httplib2.Http()
    result = h.request(realurl, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps(
            'Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/logout')
def disconnect():
    """General log out for all providers"""
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['google_id']
            # del login_session['credentials']
        elif login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']
        del login_session['user_id']
        del login_session['state']
        return render_template(
            'logout.html', GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID)
    else:
        return redirect(url_for('showCatalog'))


def getUserID(email):
    """Get user ID from email"""
    try:
        user_email = login_session['email']
        session = DBSession()
        user = session.query(User).filter_by(email=user_email).one_or_none()
        session.close()
        return user.id
    except:  # noqa
        return None


def getUserInfo(user_id):
    """Get user information by ID"""
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one_or_none()
    session.close()
    return user


def createUser(login_session):
    """Create a new user"""
    session = DBSession()
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(
        email=login_session['email']).one_or_none()
    session.close()
    return user.id


@app.route('/')
@app.route('/catalog/')
def showCatalog():
    """Show catalog"""
    session = DBSession()
    countries = session.query(Country).order_by(asc(Country.name))
    wines = session.query(Wine, Country.name).join(Country)
    session.close()
    if 'username' not in login_session:
        loggedInUsername = False
    else:
        loggedInUsername = login_session['username']
    return render_template('catalog.html',
                           countries=countries, wines=wines,
                           loggedInUsername=loggedInUsername)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('showLogin'))
    return decorated_function


@app.route('/country/new/', methods=['GET', 'POST'])
@login_required
def newCountry():
    """Create a new country"""
    # The user must be logged in to create a country
    # but the user_id is not stored like it is for a wine
    if request.method == 'POST':
        newCountry = Country(name=request.form['name'])
        session = DBSession()
        session.add(newCountry)
        session.commit()
        session.close()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newCountry.html')


@app.route('/wine/new/', methods=['GET', 'POST'])
@login_required
def newWine():
    """Create a new wine"""
    session = DBSession()
    countries = session.query(Country).order_by(asc(Country.name))
    login_user_id = login_session['user_id']
    if request.method == 'POST':
        newWine = Wine(
            country_id=request.form['country_id'],
            name=request.form['name'],
            year=request.form['year'],
            price=request.form['price'],
            rating=request.form['rating'],
            description=request.form['description'],
            user_id=login_user_id
            )
        session.add(newWine)
        session.commit()
        session.close()
        return redirect(url_for('showCatalog'))
    else:
        session.close()
        return render_template('newWine.html', countries=countries)


@app.route('/wine/<int:wine_id>/edit/', methods=['GET', 'POST'])
@login_required
def editWine(wine_id):
    """Edit a wine"""
    session = DBSession()
    wineToEdit = session.query(Wine).filter_by(id=wine_id).one_or_none()
    if wineToEdit.user_id != login_session['user_id']:
        return render_template('unauthorized.html')
    countries = session.query(Country).order_by(asc(Country.name))
    if request.method == 'POST':
        if request.form['country_id']:
            wineToEdit.country_id = request.form['country_id']
        if request.form['name']:
            wineToEdit.name = request.form['name']
        if request.form['year']:
            wineToEdit.year = request.form['year']
        if request.form['price']:
            wineToEdit.price = request.form['price']
        if request.form['rating']:
            wineToEdit.rating = request.form['rating']
        if request.form['description']:
            wineToEdit.description = request.form['description']
        session.add(wineToEdit)
        session.commit()
        session.close()
        return redirect(url_for('showCatalog'))
    else:
        session.close()
        return render_template('editWine.html',
                               wine_id=wine_id, item=wineToEdit,
                               countries=countries)


@app.route('/wine/<int:wine_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteWine(wine_id):
    """Delete a wine"""
    session = DBSession()
    wineToDelete = session.query(Wine).filter_by(id=wine_id).one_or_none()
    if wineToDelete.user_id != login_session['user_id']:
        return render_template('unauthorized.html')
    if request.method == 'POST':
        session.delete(wineToDelete)
        session.commit()
        session.close()
        return redirect(url_for('showCatalog'))
    else:
        session.close()
        return render_template('deleteWine.html', item=wineToDelete)


@app.route('/catalog/json')
def catalogJSON():
    """Generate a JSON version of the catalog"""
    session = DBSession()
    catalog = session.query(Wine).all()
    session.close()
    return jsonify(wines=[wine.serialize for wine in catalog])


@app.route('/countries/json')
def countriesJSON():
    """Generate a JSON version of the country list"""
    session = DBSession()
    countries = session.query(Country).all()
    session.close()
    return jsonify(countries=[country.serialize for country in countries])


@app.route('/wine/<int:wine_id>/json')
def wineJSON(wine_id):
    """Generate a JSON version of the wine requested"""
    session = DBSession()
    wine = session.query(Wine).filter_by(id=wine_id).one_or_none()
    session.close()
    if wine:
        return jsonify(wine=[wine.serialize])
    else:
        return 'No wine with that id'


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
