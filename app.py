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

import time


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
    return render_template('pages/signal_investors.html',  signal_query=session.get("signal_query"))

@app.route('/linkedin_investors')
@login_required
def linkedin_investors():
    return render_template('pages/linkedin_investors.html',  linkedin_query=session.get("linkedin_query"))


### API ROUTES
# Signal_Investors Route
@app.route('/api/investors/signal', methods=["POST"])
@login_required
def handle_signal_investors():
    try:
        query = {}
        body = request.get_json()
        
        # Save Query to Session
        add_to_session("signal_query", body)

        min_sweet_spot = body.get("min_sweet_spot")
        max_sweet_spot = body.get("max_sweet_spot")
        
        newstage = body.get("newstage")
        
        position = body.get("position")
        
        stage = body.get("stage")

        profile_name = body.get("profile_name")

        try:
            stage_match_all = body.get("stage_match_all")
        except:
            pass
        
        min_invs_connect = body.get("min_invs_connect")
        max_invs_connect = body.get("max_invs_connect")

        #sweet spot filter
        if (min_sweet_spot and min_sweet_spot != "") or (max_sweet_spot and max_sweet_spot != ""):
            query["Sweet Spot"] = {}
            query["Sweet Spot"]["$exists"] = True

        if min_sweet_spot and min_sweet_spot != "":
            query["Sweet Spot"]['$gte'] = int(min_sweet_spot)

        if max_sweet_spot and max_sweet_spot != "":
            query["Sweet Spot"]['$lte'] = int(max_sweet_spot) 
        
        #position filter 
        if position and position != "":
               query["Position"] = { "$regex": str(position) , }
                
        #stage filter if it only selected without ranking filter selector 
        if newstage and len(newstage) > 0:
                                
            newstageitems=''
            
            for sitem in range(len(newstage)):
                #list that have no records at all and will cause errors
                if sitem < (len(newstage)-1):
                  newstageitems=  newstageitems + str(newstage[sitem]) +"|"
                else :
                  newstageitems = newstageitems + str(newstage[sitem])
                    
            query["Sector & Stage Rankings"] = { "$regex": str(newstageitems) }
            
            #for multiple selection get first selection (first element on list)
            #query["Sector & Stage Rankings"] = { "$regex": str(newstage[0]) , "$options" : "$" }

            #single selection  (not a list)
            #query["Sector & Stage Rankings"] = { "$regex": str(newstage) , }
            


        if stage and len(stage) > 0:
            #match any
            query["Sector & Stage Rankings"] = { "$in": stage }
            
            #match all
            if stage_match_all:
              query["Sector & Stage Rankings"] = { "$all": stage }

        #combine stage(newstage) and sectors&stage rankings(stage) filters when exist
        #because the last code is the one that impacts the final query for the same object int his example 'stage
                
        #new stage filter
        if newstage and len(newstage) > 0 and stage and len(stage) > 0:
           
            newstageitems=''

            for sitem in range(len(newstage)):
                #list that have no records at all and will cause errors
                if sitem < (len(newstage)-1):
                  newstageitems=  newstageitems + str(newstage[sitem]) +"|"
                else :
                  newstageitems = newstageitems + str(newstage[sitem])
            
            #oldstage match any
            query["Sector & Stage Rankings"] = { "$in": stage,"$regex": str(newstageitems) }
            
            #oldstage match all
            if stage_match_all:
                  query["Sector & Stage Rankings"] = { "$all": stage,"$regex": str(newstageitems) }

            
            
        if (min_invs_connect and min_invs_connect != "") or (max_invs_connect and max_invs_connect != ""):
            query["Investing connections amount"] = {}
            query["Investing connections amount"]["$exists"] = True

        if min_invs_connect and min_invs_connect != "":
            query["Investing connections amount"]['$gte'] = int(min_invs_connect)

        if max_invs_connect and max_invs_connect != "":
            query["Investing connections amount"]['$lte'] = int(max_invs_connect)
            
        if profile_name and profile_name != "":
            query["Profile Name"] = { "$regex": profile_name, "$options" :'i' }
            
        
        #investment range filter
        min_investment = body.get("min_investment")
        max_investment = body.get("max_investment")
        
        if min_investment and min_investment != "" and max_investment and max_investment != "":
            query["min_investment"] = {}
            query["min_investment"]["$exists"] = True
            query["max_investment"] = {}
            query["max_investment"]["$exists"] = True

            query["min_investment"]['$gte'] = int(min_investment)
            query["max_investment"]['$gte'] = int(min_investment)

            query["min_investment"]['$lte'] = int(max_investment) 
            query["max_investment"]['$lte'] = int(max_investment) 



        print("MongoDB Signal Query : "+ str(query))

        #Hamed is data only
        #signal_invest_data = db.signalNFXInvestors
        
        #merged data from hesham and hamed 
        signal_invest_data = db.signalMerge
        
        #Logic for pagination
        offset = int(request.args.get('offset',0))
        limit = 10
        
        starting_id = signal_invest_data.find(query).sort('_id', pymongo.ASCENDING)

        try:
          last_id = starting_id[offset]['_id']
        except:
          last_id = None
        
        # Counting Query Documents Vs. Total Documents
        query_count = signal_invest_data.count_documents(query)
        
        total_count = signal_invest_data.count_documents({})

        add_to_session("signal_query_count", query_count)
        
        add_to_session("signal_total_count", total_count)

        if query_count < total_count:
          add_to_session("signal_mongodb_query", query)
        else:
          add_to_session("signal_mongodb_query", {})
    
        next_chunk = offset + limit
        prev_chunk = 0
        if offset - limit > 0:
            prev_chunk = offset - limit

        if last_id:
          json_data = signal_invest_data.find({**query, **{"_id": {'$gte': last_id}}}, limit=limit).sort('_id', pymongo.ASCENDING)
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


# Count_Investors Route
@app.route('/api/investors/signal/count', methods=["POST"])
@login_required
def count_signal_investors():
  try:
    signal_invest_data = db.signalMerge
    body = request.get_json()
    field = body.get("field")
    query = body.get("query")
    count = signal_invest_data.count_documents({ field: { "$regex": query, "$options" :'i' } })
    return jsonify({
      "count" : count,
    })
  except:
    return jsonify({
      "count" : 0,
    })

# Get Filters Options
@app.route('/api/investors/signal/options')
@login_required
def signal_filter_options():
  try:
    signal_invest_data = db.signalMerge
    try:
      stage_options = list(signal_invest_data.distinct("Sector & Stage Rankings"))
      stage_options = [x for x in stage_options if type(x) == str]
      position_options = list(signal_invest_data.distinct("Position"))
      position_options = [x for x in position_options if type(x) == str]
    except:
      stage_options = [] 
      position_options = []
    return jsonify({
      "options" : {
        "stage_options" : stage_options,
        "position_options" : position_options,
      }
    })
  except:
    return jsonify({
      "options" : {},
    })

# Signal_Investors Route
@app.route('/api/investors/linkedin', methods=["POST"])
@login_required
def handle_linkedin_investors():

    try:

        query = {}
        body = request.get_json()

        #LinkedIn Data 
        linkedin_invest_data = db.signalMerge        
        
        # Save Query to Session
        add_to_session("linkedin_query", body)

        signal_invest_data = db.signalMerge

        signal_mongodb_query = session["signal_mongodb_query"]

        has_linkedin_query = {"$and":[{"Linkedin Profile Attached": {"$ne": None}}, {"Linkedin Profile Attached": {"$ne": ""}}]}

        person_ids_list = signal_invest_data.distinct("person_id", {**signal_mongodb_query, **has_linkedin_query})

        if signal_mongodb_query != {}:
          query["person_id"] = { "$in": person_ids_list }
        else:
          query = {**has_linkedin_query}

        has_linkedin_count = len(person_ids_list)
        
        no_linkedin_count = session["signal_query_count"] - has_linkedin_count

        min_sweet_spot = body.get("min_sweet_spot")
        max_sweet_spot = body.get("max_sweet_spot")
        
        newstage = body.get("newstage")
        
        position = body.get("position")
        
        stage = body.get("stage")

        profile_name = body.get("profile_name")

        try:
            stage_match_all = body.get("stage_match_all")
        except:
            pass
        
        min_invs_connect = body.get("min_invs_connect")
        max_invs_connect = body.get("max_invs_connect")

        #sweet spot filter
        if (min_sweet_spot and min_sweet_spot != "") or (max_sweet_spot and max_sweet_spot != ""):
            query["Sweet Spot"] = {}
            query["Sweet Spot"]["$exists"] = True

        if min_sweet_spot and min_sweet_spot != "":
            query["Sweet Spot"]['$gte'] = int(min_sweet_spot)

        if max_sweet_spot and max_sweet_spot != "":
            query["Sweet Spot"]['$lte'] = int(max_sweet_spot) 
        
        #position filter 
        if position and position != "":
               query["Position"] = { "$regex": str(position) , }
                
        #stage filter if it only selected without ranking filter selector 
        if newstage and len(newstage) > 0:
                                
            newstageitems=''
            
            for sitem in range(len(newstage)):
                #list that have no records at all and will cause errors
                if sitem < (len(newstage)-1):
                  newstageitems=  newstageitems + str(newstage[sitem]) +"|"
                else :
                  newstageitems = newstageitems + str(newstage[sitem])
                    
            query["Sector & Stage Rankings"] = { "$regex": str(newstageitems) }
            
            #for multiple selection get first selection (first element on list)
            #query["Sector & Stage Rankings"] = { "$regex": str(newstage[0]) , "$options" : "$" }

            #single selection  (not a list)
            #query["Sector & Stage Rankings"] = { "$regex": str(newstage) , }
            


        if stage and len(stage) > 0:
            #match any
            query["Sector & Stage Rankings"] = { "$in": stage }
            
            #match all
            if stage_match_all:
              query["Sector & Stage Rankings"] = { "$all": stage }

        #combine stage(newstage) and sectors&stage rankings(stage) filters when exist
        #because the last code is the one that impacts the final query for the same object int his example 'stage
                
        #new stage filter
        if newstage and len(newstage) > 0 and stage and len(stage) > 0:
           
            newstageitems=''

            for sitem in range(len(newstage)):
                #list that have no records at all and will cause errors
                if sitem < (len(newstage)-1):
                  newstageitems=  newstageitems + str(newstage[sitem]) +"|"
                else :
                  newstageitems = newstageitems + str(newstage[sitem])
            
            #oldstage match any
            query["Sector & Stage Rankings"] = { "$in": stage,"$regex": str(newstageitems) }
            
            #oldstage match all
            if stage_match_all:
                  query["Sector & Stage Rankings"] = { "$all": stage,"$regex": str(newstageitems) }

            
            
        if (min_invs_connect and min_invs_connect != "") or (max_invs_connect and max_invs_connect != ""):
            query["Investing connections amount"] = {}
            query["Investing connections amount"]["$exists"] = True

        if min_invs_connect and min_invs_connect != "":
            query["Investing connections amount"]['$gte'] = int(min_invs_connect)

        if max_invs_connect and max_invs_connect != "":
            query["Investing connections amount"]['$lte'] = int(max_invs_connect)
            
        if profile_name and profile_name != "":
            query["Profile Name"] = { "$regex": profile_name, "$options" :'i' }
            
        
        #investment range filter
        min_investment = body.get("min_investment")
        max_investment = body.get("max_investment")
        
        if min_investment and min_investment != "" and max_investment and max_investment != "":
            query["min_investment"] = {}
            query["min_investment"]["$exists"] = True
            query["max_investment"] = {}
            query["max_investment"]["$exists"] = True

            query["min_investment"]['$gte'] = int(min_investment)
            query["max_investment"]['$gte'] = int(min_investment)

            query["min_investment"]['$lte'] = int(max_investment) 
            query["max_investment"]['$lte'] = int(max_investment) 


        #Logic for pagination
        offset = int(request.args.get('offset',0))
        limit = 10

        start_time = time.time()

        starting_id = linkedin_invest_data.find(query).sort('_id', pymongo.ASCENDING)

        try:
          last_id = starting_id[offset]['_id']
        except:
          last_id = None
        
        print("Slow Part 1 --- %s seconds ---" % (time.time() - start_time))
        start_time_2 = time.time()    
        
        # Counting Query Documents Vs. Total Documents
        query_count = linkedin_invest_data.count_documents(query)


        print("Slow Part 2 --- %s seconds ---" % (time.time() - start_time_2))
        total_count = session["signal_query_count"]
    
        next_chunk = offset + limit
        prev_chunk = 0
        if offset - limit > 0:
            prev_chunk = offset - limit


        if last_id:
          json_data = linkedin_invest_data.find({**query, **{"_id": {'$gte': last_id}}}, limit=limit).sort('_id', pymongo.ASCENDING)
        else:
          json_data = []        
            

        return jsonify({
            "investors": loads(dumps(json_data)),
            "total_count": total_count,
            "query_count": query_count,
            "limit": limit,
            "next_chunk": next_chunk,
            "prev_chunk": prev_chunk,
            "has_linkedin_count": has_linkedin_count,
            "no_linkedin_count": no_linkedin_count,
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
            "has_linkedin_count": 0,
            "no_linkedin_count": 0,
        })


# Count_Investors Route
@app.route('/api/investors/linkedin/count', methods=["POST"])
@login_required
def count_linkedin_investors():
  try:
    linkedin_invest_data = db.signalMerge
    body = request.get_json()
    field = body.get("field")
    query = body.get("query")
    count = linkedin_invest_data.count_documents({ field: { "$regex": query, "$options" :'i' } })
    return jsonify({
      "count" : count,
    })
  except:
    return jsonify({
      "count" : 0,
    })

# Get Filters Options
@app.route('/api/investors/linkedin/options')
@login_required
def linkedin_filter_options():
  try:
    linkedin_invest_data = db.signalMerge
    try:
      stage_options = list(linkedin_invest_data.distinct("Sector & Stage Rankings"))
      stage_options = [x for x in stage_options if type(x) == str]
      position_options = list(linkedin_invest_data.distinct("Position"))
      position_options = [x for x in position_options if type(x) == str]
    except:
      stage_options = [] 
      position_options = []
    return jsonify({
      "options" : {
        "stage_options" : stage_options,
        "position_options" : position_options,
      }
    })
  except:
    return jsonify({
      "options" : {},
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
    app.run(host='0.0.0.0', port=1337)
 
