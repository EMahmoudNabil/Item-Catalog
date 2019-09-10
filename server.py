from flask import Flask, render_template
from flask import request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
import json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests

app = Flask(__name__)

engine = create_engine('postgresql://catalog:1234@localhost/itemcatalogpsql')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


def createUser(login_session):

    """This function takes a login session information
    of a user and make an entry for that user in the database

    Parameters:
    login_session (dictionary): the login session information about the user

    Returns:
    int: the ID of the newly created user
    """
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """This function takes a user ID that exists in our database
    and return the user itself with all its information

    Parameters:
    user_id (int): the ID of the user in the database

    Returns:
    user: the user object
    """
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """This function takes a user email and returns its ID if the user
    exists in our database, otherwise it returns None

    Parameters:
    email (string): the email of the user

    Returns:
    int: the ID of the user (if found)
    None : if the user isn't found
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/')
def showCategoriesAndLatestitems():
    """This function is responsible for rendering the home page template with
    the required data (all different categories and the latest added items)

    Returns:
    template: a HTML template of the home page
    """
    categories = session.query(Category)
    # only the latest 6 items will be shown
    latestItems = session.query(Category, Item)\
        .filter(Category.id == Item.category_id)\
        .order_by(desc(Item.last_modification))\
        .limit(6)
    return render_template('homepage.html',
                           categories=categories,
                           latestItems=latestItems)


@app.route('/categories/JSON')
def showCategoriesandItems():
    """This function is responsible to give the data of this API endpoint
    as a JSON object, the data being sent in this function is
    all the categories accompanied by their items

    Returns:
    JSON object: all the categories with their items
    """
    categories = session.query(Category)
    return jsonify(categories=[category.serialize for category in categories.all()])


@app.route('/login')
def showLogin():
    """This function is responsible for creating an anti-forgery state token
    to prevent cross-site request forgery attacks, and rendering the login page

    Returns:
    template: an HTML template of the login page
    """
    # create anti-forgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """This function handles the code sent back from the callback method, and
    make some validations and verifications like validating the state token and
    the access token.
    It also stores the access token in the user login session and save all user's data
    int the login session as well.


    Returns:
    template: a HTML template that contains the user data to welcome the user after logging in
    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # if a user doesn't exist, make an entry for it
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px;'\
              'height: 300px;'\
              'border-radius: 150px;'\
              '-webkit-border-radius: 150px;'\
              '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """This function is responsible for disconnecting the user from
    out website, it tells the server to reject the acess token, and it deletes
    all the user data from the login session

    Returns:
    response: a message to the user that they are successfully disconnected or an error happened
    """
    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/catalog/<category_name>/items/')
def showCategoryItems(category_name):
    """This function takes a category name and returns a HTML template page
    that shows the items of that category to the user

    Parameters:
    category_name (string): the category name that we want to see its items

    Returns:
    template: an HTML template containing the required data
    """
    categories = session.query(Category)
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id)
    return render_template('category_items.html', 
                           categories=categories, 
                           items=items, 
                           category_name=category_name)


@app.route('/catalog/<category_name>/items/JSON/')
def showCategoryItemsJSON(category_name):
    """This function is responsible to give the data of this API endpoint
    as a JSON object, the data being sent in this function is
    all the items of a specific category.

    Parameters:
    category_name (string): the category name that we want its items

    Returns:
    JSON object: the category items
    """
    chosenCategory = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=chosenCategory.id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalog/<category_name>/<item_name>/')
def showItemsDescription(category_name, item_name):
    """This function takes a category name and an item name and shows the user
    the description of that item

    Parameters:
    category_name (string): the category of the chosen item
    item_name (string): the chosen item

    Returns:
    template: a HTML template containing the item description
    """
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(category_id=category.id, name=item_name).one()
    return render_template('item_description.html', item=item)


@app.route('/catalog/<category_name>/<item_name>/JSON')
def showItemsDescriptionJSON(category_name, item_name):
    """This function is responsible to give the data of this API endpoint
    as a JSON object, the data being sent in this function is
    an item as a JSON object

    Parameters:
    category_name (string): the category of the chosen item
    item_name (string): the chosen item
    Returns:
    JSON object: a JSON object containing the item
    """
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(category_id=category.id, name=item_name).one()
    return jsonify(Item=item.serialize)


@app.route('/catalog/item/new', methods=['GET', 'POST'])
def newCatalogItem():
    """This function is responsible for making a new item


    Returns:
    template: a HTML template of the page that the user will provide the item information in (GET)
    template: a HTML template of the items after the item has been added (POST)
    """

    # allow only the authenticated users
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form.get('name', None)
        description = request.form.get('description', None)
        chosenCategory = request.form.get('category', None)
        exist = session.query(Item).filter_by(name=name).first()
        # make sure that there's no item in the database with the same name
        if exist is None:
            category = session.query(Category).filter_by(name=chosenCategory).one()
            newItem = Item(name=name, 
                           description=description, 
                           category_id=category.id, 
                           user_id=login_session['user_id'])
            session.add(newItem)
            session.commit()
            flash('New %s Item Successfully Created' % chosenCategory)
            return redirect(url_for('showCategoriesAndLatestitems'))
        else:
            print("name mtkrr")

            redirect(url_for('newCatalogItem'))
            flash('This item name already exist')
            return

    else:
        categories = session.query(Category)
        return render_template('add_item.html', categories=categories)


@app.route('/catalog/<item_name>/edit', methods=['GET', 'POST'])
def editCatalogItem(item_name):
    """This function is responsible for updating the new information of an item
    after it has been edited

    Parameters:
    item_name (string): the edited item

    Returns:
    template: a HTML template of the page that the user will edit the item information in (GET)
    template: a HTML template of the items after the item has been edited (POST)
    """
    # allow only authenticated users
    if 'username' not in login_session:
        return redirect('/login')

    item = session.query(Item).filter_by(name=item_name).one()
    categories = session.query(Category)
    category = session.query(Category).filter_by(id=item.category_id).one()
    # allow only the creator of the item to edit it
    if login_session['user_id'] != item.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit this catalog item. Please create your own items in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        print("hereeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        item.name = request.form['name']
        item.description = request.form['description']
        chosenCategory = session.query(Category).filter_by(name=request.form['category']).one()
        item.category_id = chosenCategory.id
        session.add(item)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showItemsDescription', 
                        item_name=item.name, 
                        category_name=chosenCategory.name))

    else:
        return render_template('edit_item.html', 
                               item=item, 
                               categories=categories, 
                               category_name=category.name)


@app.route('/catalog/<item_name>/delete', methods=['GET', 'POST'])
def deleteCatalogItem(item_name):
    """This function is responsible for deleting an item

    Parameters:
    item_name (string): the item we want to delete

    Returns:
    template: a HTML template of the page that the user will delete the item in (GET)
    template: a HTML template of the items after the item has been deleted (POST)
    """
    # allow only authenticated users
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Item).filter_by(name=item_name).one()
    category = session.query(Category).filter_by(id=item.category_id).one()
    # allow only the creator of the item to delete it
    if login_session['user_id'] != item.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit this catalog item. Please create your own items in order to edit.');}</script><body onload='myFunction()''>" 
    if request.method == 'POST':
        session.delete(item)
        flash('%s Successfully Deleted' % item.name)
        session.commit()
        return redirect(url_for('showCategoriesAndLatestitems'))

    else:
        return render_template('delete_item.html', item=item, category_name=category.name)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
