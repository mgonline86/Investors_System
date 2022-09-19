import os
import requests
from dotenv import load_dotenv

load_dotenv()  # loading enviromental variable from .env files
from flask import Flask, jsonify, render_template, request, session, flash, abort
from flask_mongoengine import MongoEngine
from flask_user import login_required, roles_required, UserManager, UserMixin
from config_user import ConfigClass, DB_USERNAME
from wtforms import validators
from wtforms import StringField
from flask_user.forms import RegisterForm
from flask_user.translation_utils import lazy_gettext as _
from db_setup import db
from bson.json_util import dumps
from json import loads
import pymongo

API_KEY = os.getenv('API_KEY')
API_PASS = os.getenv('API_PASS')
API_TOKEN = os.getenv('API_TOKEN')
API_HOST = os.getenv('API_HOST')
# SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
# app.secret_key = SECRET_KEY

app.config.from_object(__name__+'.ConfigClass')

# Setup Flask-MongoEngine
db_user = MongoEngine(app)

# Define the User document.
# NB: Make sure to add flask_user UserMixin !!!
class User(db_user.Document, UserMixin):
    active = db_user.BooleanField(default=False) # So User Needs Admin Approval 

    # User authentication information
    email = db_user.StringField(default='')
    email_confirmed_at = db_user.DateTimeField()
    # username = db_user.StringField(default='')
    password = db_user.StringField()

    # User information
    first_name = db_user.StringField(default='')
    last_name = db_user.StringField(default='')

    # Relationships
    roles = db_user.ListField(db_user.StringField(), default=[])

class UserInvitation(db_user.Document):
    email = db_user.StringField(default='')
    invited_by_user_id = db_user.ObjectIdField()
   
# Customize the Register form:
class CustomRegisterForm(RegisterForm):
    first_name = StringField(_('First name'), validators=[
        validators.DataRequired(_('First name is required'))])
    last_name = StringField(_('Last name'), validators=[
        validators.DataRequired(_('Last name is required'))])

# Customize Flask-User
class CustomUserManager(UserManager):

  def customize(self, app):

    # Configure customized forms
    self.RegisterFormClass = CustomRegisterForm

  # Making user invitation limited to admin role only
  @roles_required('admin')
  def invite_user_view(self):
    return super().invite_user_view()
    
            
# Setup Flask-User and specify the User data-model
user_manager = CustomUserManager(app, db_user, User, UserInvitationClass=UserInvitation)

# Use this function to add a Variable to Session
def add_to_session(key, value):
    session[key] = value


### HTML ROUTES

#Homepage
@app.route('/')
@login_required
def index():
    return render_template('pages/home.html')

@app.route('/signal_investors')
@login_required
def signal_investors():
    return render_template('pages/signal_investors.html')


### API ROUTES
# Signal_Investors Route
@app.route('/api/investors/signal', methods=["POST"])
@login_required
def handle_signal_investors():
    try:
        query = {}
        body = request.get_json()
        stage = body.get("stage")
        min_invs_connect = body.get("min_invs_connect")
        max_invs_connect = body.get("max_invs_connect")

        ### I commented min and max invest until fixing data type in db from str to int ###

        # min_investment = body.get("min_investment")
        # max_investment = body.get("max_investment")

        if stage and len(stage) > 0:
            query["stage"] = { "$all": stage }
        
        if min_invs_connect and min_invs_connect != "":
            query["Investing Connections"] = {"$exists": True, '$gte': int(min_invs_connect)}
        
        if max_invs_connect and max_invs_connect != "":
            query["Investing Connections"] = {"$exists": True, '$lte': int(max_invs_connect)}
        
        # if min_investment and min_investment != "":
        #     query["min_investment"] = {"$exists": True, '$gte': int(min_investment)}
        
        # if max_investment and max_investment != "":
        #     query["max_investment"] = {"$exists": True, '$lte': int(max_investment)}
        

        signal_invest_data = db.signalNFXInvestors
        
        #Logic for pagination
        offset = int(request.args.get('offset',0))
        limit = 10
        
        starting_id = signal_invest_data.find(query).sort('_id', pymongo.ASCENDING)
        try:
          last_id = starting_id[offset]['_id']
        except:
          last_id = None

        next_chunk = offset + limit
        prev_chunk = 0
        if offset - limit > 0:
            prev_chunk = offset - limit

        # Counting Query Documents Vs. Total Documents
        query_count = signal_invest_data.count_documents(query)
        total_count = signal_invest_data.count_documents({})
        
        if last_id:
          json_data = signal_invest_data.find({**query, **{"_id": {'$gte': last_id}}}, limit=limit)
        else:
          json_data = []

        return jsonify({
            "investors": loads(dumps(json_data)),
            "total_count": total_count,
            "query_count": query_count,
            "limit": limit,
            "next_chunk": next_chunk,
            "prev_chunk": prev_chunk,
        })
    except Exception as e:
        print(e)
        return jsonify({
            "investors": [],
            "total_count": 0,
            "query_count": 0,
            "limit": 0,
            "next_chunk": 0,
            "prev_chunk": 0,
        })



# User-Routes
@app.route("/admin/users_page")
@roles_required('admin')
def view_users():
  return render_template('pages/admin_users.html')

@app.route("/user")
@roles_required('admin')
def all_users():
  try:
    return jsonify({
      "success" : True,
      "users" : User.objects(),
      })
  except Exception as e:
    error_code = e.__dict__.get('_OperationFailure__code')
    error_message = e.__dict__.get('_message')
    return jsonify({
      "success" : False,
      "error" : error_message,
      "error_code" : error_code,
    })

@app.route("/user/<string:id>/alter_admin", methods=['PUT'])
@roles_required('admin')
def alter_admin(id):
  try:
    json_req = request.json
    admin_status = json_req['admin']
    admin_users_count = User.objects(roles="admin")
    user = User.objects(id=id)
    user_email= user.first().email
    if user_email == DB_USERNAME+"@yahoo.com":
        flash("Founder User must be an Admin", "error")
        return jsonify({
        "success" : False,
        "error" : "Founder User must be an Admin",
        "error_code" : 422,
        }) 
    if admin_status:
      user.update_one(add_to_set__roles=['admin'])
      return jsonify({
        "success" : True,
        "user" : user,
      })
    else:
      if len(admin_users_count) == 1:
        flash("There must be one Admin Account", "error")
        return jsonify({
        "success" : False,
        "error" : "There must be at least one Admin Account",
        "error_code" : 422,
        })      
      else:
        user.update_one(pull__roles='admin')
        return jsonify({
          "success" : True,
          "user" : user,
        })

  except Exception as e:
    error_code = e.__dict__.get('_OperationFailure__code')
    error_message = e.__dict__.get('_message')
    return jsonify({
      "success" : False,
      "error" : error_message,
      "error_code" : error_code,
    })

@app.route("/user/<string:id>", methods=['GET', 'POST', 'PUT', 'DELETE'])
@roles_required('admin')
def alter_user(id):
  if request.method == 'DELETE':
    try:
      user = User.objects(id=id)
      all_users = User.objects()
      admin_users = list(filter(lambda x: 'admin'in x['roles'], all_users))
      user_email= user.first().email
      if user_email == DB_USERNAME+"@yahoo.com":
        flash("You can't delete The Founder User", "error")
        return jsonify({
        "success" : False,
        "error" : "You can't delete The Founder User",
        "error_code" : 422,
        })  
      if (len(all_users) == 1) or (len(admin_users) == 1 and 'admin' in user.first().roles):
        flash("There must be one Admin Account", "error")
        return jsonify({
        "success" : False,
        "error" : "There must be at least one Admin Account",
        "error_code" : 422,
        })  
      else:
        user.delete()
        return jsonify({
          "success" : True,
          "user" : user,
        })      

    except Exception as e:
      error_code = e.__dict__.get('_OperationFailure__code')
      error_message = e.__dict__.get('_message')

      return jsonify({
        "success" : False,
        "error" : error_message,
        "error_code" : error_code,
      })
  else:
    abort(405)



if __name__ == '__main__':
    app.run(debug=True)
 