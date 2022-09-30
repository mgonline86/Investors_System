import os
import requests
from dotenv import load_dotenv

load_dotenv()  # loading enviromental variable from .env files
from flask import Flask, jsonify, render_template, request, session, flash, abort
from flask_mongoengine import MongoEngine
from flask_user import login_required, roles_required, UserManager, UserMixin, current_user
from config_user import ConfigClass, DB_USERNAME
from wtforms import validators
from wtforms import StringField
from flask_user.forms import RegisterForm
from flask_user.translation_utils import lazy_gettext as _
from db_setup import db
from bson.json_util import dumps
from json import loads
import pymongo
import json

import time

### DECLARING GLOBAL VARIABLES ###

ENVIRONMENT = os.getenv('ENVIRONMENT')

## DATABASES ##

#Hamed is data only
#SIGNAL_INVEST_DATA = db.signalNFXInvestors

#merged data from hesham and hamed
SIGNAL_INVEST_DATA = db.signalMerge

#LinkedIn Data 
LINKEDIN_INVEST_DATA = db.signalMerge 

### APP SETUP ###
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

    # Filters
    filters = db_user.DictField(default={})

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
    user = User.objects(id=current_user.id).first()
    signal_query = user.filters.get("signal_front")
    # return render_template('pages/signal_investors.html',  signal_query=session.get("signal_query"))
    return render_template('pages/signal_investors.html',  signal_query=signal_query)

@app.route('/linkedin_investors')
@login_required
def linkedin_investors():
    user = User.objects(id=current_user.id).first()
    linkedin_query = user.filters.get("linkedin_front")
    # return render_template('pages/linkedin_investors.html',  linkedin_query=session.get("linkedin_query"))
    return render_template('pages/linkedin_investors.html',  linkedin_query=linkedin_query)


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
        user = User.objects(id=current_user.id).first()
        user.update(set__filters__signal_front=body)

        min_sweet_spot = body.get("min_sweet_spot")
        max_sweet_spot = body.get("max_sweet_spot")
        
        newstage = body.get("newstage")
        
        position = body.get("position")
        
        stage = body.get("stage")

        # profile_name = body.get("profile_name")

        new_profile_name = body.get("new_profile_name")

        firm = body.get("firm")

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
            
        # if profile_name and profile_name != "":
        #     query["Profile Name"] = { "$regex": profile_name, "$options" :'i' }
            
        if new_profile_name and new_profile_name != "":
            query["Profile Name"] = new_profile_name
            
        if firm and firm != "":
            query["Firm"] = firm
            
        
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

        
        # Counting Query Documents Vs. Total Documents
        query_count = SIGNAL_INVEST_DATA.count_documents(query)
        
        total_count = SIGNAL_INVEST_DATA.count_documents({})
        
        add_to_session("signal_total_count", total_count)

        if query_count < total_count:
          # add_to_session("signal_mongodb_query", query)
          user.update(set__filters__signal_back=json.dumps(query))

        else:
          # add_to_session("signal_mongodb_query", {})
          user.update(set__filters__signal_back=json.dumps({}))


        # Get Final Results Logic
        final_Results = str(request.args.get('finalResults',False))
        if final_Results == "true":
          #Final Database
          final_database = db.signalMerge
          final_query = json.loads(user.filters.get("linkedin_back"))
          final_person_ids = final_database.distinct("person_id", final_query)
          query["person_id"] = { "$in": final_person_ids }
          query_count = SIGNAL_INVEST_DATA.count_documents(query)

        
        #Logic for pagination
        offset = int(request.args.get('offset',0))
        limit = 10
        
        starting_id = SIGNAL_INVEST_DATA.find(query).sort('_id', pymongo.ASCENDING)

        try:
          last_id = starting_id[offset]['_id']
        except:
          last_id = None

        print("MongoDB Signal Query : "+ str(query))
    
        next_chunk = offset + limit
        prev_chunk = 0
        if offset - limit > 0:
            prev_chunk = offset - limit

        if last_id:
          json_data = SIGNAL_INVEST_DATA.find({**query, **{"_id": {'$gte': last_id}}}, limit=limit).sort('_id', pymongo.ASCENDING)
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
    body = request.get_json()
    field = body.get("field")
    query = body.get("query")
    count = SIGNAL_INVEST_DATA.count_documents({ field: { "$regex": query, "$options" :'i' } })
    return jsonify({
      "count" : count,
    })
  except:
    return jsonify({
      "count" : 0,
    })


# Search Field Options Route
@app.route('/api/investors/signal/search', methods=["POST"])
@login_required
def search_signal_investors():
  try:
    body = request.get_json()
    field = body.get("field")
    query = body.get("query")
    limit = body.get("limit")
    result = SIGNAL_INVEST_DATA.distinct(field, { field: { "$regex": f'^{query}', "$options" :'i' } })[:limit]
    result = [x for x in result if type(x) == str]
    return jsonify({
      "result" : result,
    })
  except:
    return jsonify({
      "result" : [],
    })

# Get Filters Options
@app.route('/api/investors/signal/options')
@login_required
def signal_filter_options():
  try:
    try:
      stage_options = list(SIGNAL_INVEST_DATA.distinct("Sector & Stage Rankings"))
      stage_options = [x for x in stage_options if type(x) == str]
      position_options = list(SIGNAL_INVEST_DATA.distinct("Position"))
      position_options = [x for x in position_options if type(x) == str]
      new_profile_name_options = SIGNAL_INVEST_DATA.find(
        {"Profile Name": {"$ne": None}},
        {"_id":0, "Profile Name":1},
        limit=20,
        sort=[('Profile Name', pymongo.ASCENDING)]
      )
      new_profile_name_options = [x["Profile Name"] for x in new_profile_name_options if type(x["Profile Name"]) == str]
      firm_options = SIGNAL_INVEST_DATA.distinct("Firm")[:20]
      firm_options = [x for x in firm_options if type(x) == str]
    except:
      stage_options = [] 
      position_options = []
      new_profile_name_options = []
      firm_options = []
    return jsonify({
      "options" : {
        "stage_options" : stage_options,
        "position_options" : position_options,
        "new_profile_name_options" : new_profile_name_options,
        "firm_options" : firm_options,
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
        user = User.objects(id=current_user.id).first()

        query = {}
        body = request.get_json() 
        
        # Save Query to Session
        # add_to_session("linkedin_query", body)
        user.update(set__filters__linkedin_front=body)
        

        # signal_mongodb_query = session["signal_mongodb_query"]
        signal_mongodb_query = json.loads(user.filters["signal_back"])


        has_linkedin_query = {"$and":[{"Linkedin Profile Attached": {"$ne": None}}, {"Linkedin Profile Attached": {"$ne": ""}}]}

        person_ids_list = SIGNAL_INVEST_DATA.distinct("person_id", {**signal_mongodb_query, **has_linkedin_query})

        if signal_mongodb_query != {}:
          query["person_id"] = { "$in": person_ids_list }
        else:
          query = {**has_linkedin_query}

        has_linkedin_count = len(person_ids_list)

        signal_query_count = SIGNAL_INVEST_DATA.count_documents(signal_mongodb_query)        
        
        no_linkedin_count = signal_query_count - has_linkedin_count

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

        starting_id = LINKEDIN_INVEST_DATA.find(query).sort('_id', pymongo.ASCENDING)

        try:
          last_id = starting_id[offset]['_id']
        except:
          last_id = None
        
        print("Slow Part 1 --- %s seconds ---" % (time.time() - start_time))
        start_time_2 = time.time()    
        
        # Counting Query Documents Vs. Total Documents
        query_count = LINKEDIN_INVEST_DATA.count_documents(query)


        print("Slow Part 2 --- %s seconds ---" % (time.time() - start_time_2))
        total_count = signal_query_count
    
        user.update(set__filters__linkedin_back=json.dumps(query))

        next_chunk = offset + limit
        prev_chunk = 0
        if offset - limit > 0:
            prev_chunk = offset - limit


        if last_id:
          json_data = LINKEDIN_INVEST_DATA.find({**query, **{"_id": {'$gte': last_id}}}, limit=limit).sort('_id', pymongo.ASCENDING)
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
    body = request.get_json()
    field = body.get("field")
    query = body.get("query")
    count = LINKEDIN_INVEST_DATA.count_documents({ field: { "$regex": query, "$options" :'i' } })
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
    try:
      stage_options = list(LINKEDIN_INVEST_DATA.distinct("Sector & Stage Rankings"))
      stage_options = [x for x in stage_options if type(x) == str]
      position_options = list(LINKEDIN_INVEST_DATA.distinct("Position"))
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
  if ENVIRONMENT == "DEV":
    app.run(debug=True)
  else:
    app.run(host='0.0.0.0', port=1337)
 
