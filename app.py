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
# SIGNAL_INVEST_DATA = db.signalMerge
SIGNAL_INVEST_DATA = db.signalMergeUpdate1

#LinkedIn Data 
LINKEDIN_INVEST_DATA = db.signalLinkedInSample 

#Twitter Data 
TWITTER_INVEST_DATA = db.signalTwittersUpdate1 

#Angelist Data 
ANGELIST_INVEST_DATA = db.signalAngelist 

#Tail Database (Last one in line)
TAIL_DATABASE = ANGELIST_INVEST_DATA

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
    # user = User.objects(id=current_user.id).first()
    signal_query = current_user.filters.get("signal_front")
    return render_template('pages/signal_investors.html',  signal_query=signal_query)

@app.route('/linkedin_investors')
@login_required
def linkedin_investors():
    # user = User.objects(id=current_user.id).first()
    linkedin_query = current_user.filters.get("linkedin_front")
    return render_template('pages/linkedin_investors.html',  linkedin_query=linkedin_query)

@app.route('/twitter_investors')
@login_required
def twitter_investors():
    # user = User.objects(id=current_user.id).first()
    twitter_query = current_user.filters.get("twitter_front")
    return render_template('pages/twitter_investors.html',  twitter_query=twitter_query)

@app.route('/angelist_investors')
@login_required
def angelist_investors():
    # user = User.objects(id=current_user.id).first()
    angelist_query = current_user.filters.get("angelist_front")
    return render_template('pages/angelist_investors.html',  angelist_query=angelist_query)


### API ROUTES
## Signal_Investors Routes
# Signal Main Route
@app.route('/api/investors/signal', methods=["POST"])
@login_required
def handle_signal_investors():
    try:
        query = {}

        body = request.get_json()
        
        # Save Query to Session
        current_user.update(set__filters__signal_front=body)

        min_sweet_spot = body.get("min_sweet_spot")
        max_sweet_spot = body.get("max_sweet_spot")
        
        newstage = body.get("newstage")
        
        position = body.get("position")
        
        stage = body.get("stage")

        # profile_name = body.get("profile_name")

        new_profile_name = body.get("new_profile_name")

        firm = body.get("firm")

        sector_of_interest = body.get("sector_of_interest")
        
        # is_lead filter 
        is_lead = body.get("is_lead")
        if is_lead and is_lead != "":
          query["Is lead"] = True if is_lead == "t" else False

        try:
            stage_match_all = body.get("stage_match_all")
        except:
            pass
        
        min_invs_connect = body.get("min_invs_connect")
        max_invs_connect = body.get("max_invs_connect")

        #Sweet spot filter
        if (min_sweet_spot and min_sweet_spot != "") or (max_sweet_spot and max_sweet_spot != ""):
            query["Sweet spot"] = {}
            query["Sweet spot"]["$exists"] = True

        if min_sweet_spot and min_sweet_spot != "":
            query["Sweet spot"]['$gte'] = int(min_sweet_spot)

        if max_sweet_spot and max_sweet_spot != "":
            query["Sweet spot"]['$lte'] = int(max_sweet_spot) 
        
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
                    
            query["Sector & stage rankings"] = { "$regex": str(newstageitems) }
            
            #for multiple selection get first selection (first element on list)
            #query["Sector & stage rankings"] = { "$regex": str(newstage[0]) , "$options" : "$" }

            #single selection  (not a list)
            #query["Sector & stage rankings"] = { "$regex": str(newstage) , }
            


        if stage and len(stage) > 0:
            #match any
            query["Sector & stage rankings"] = { "$in": stage }
            
            #match all
            if stage_match_all:
              query["Sector & stage rankings"] = { "$all": stage }

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
            query["Sector & stage rankings"] = { "$in": stage,"$regex": str(newstageitems) }
            
            #oldstage match all
            if stage_match_all:
                  query["Sector & stage rankings"] = { "$all": stage,"$regex": str(newstageitems) }

            
            
        if (min_invs_connect and min_invs_connect != "") or (max_invs_connect and max_invs_connect != ""):
            query["Investing connections amount"] = {}
            query["Investing connections amount"]["$exists"] = True

        if min_invs_connect and min_invs_connect != "":
            query["Investing connections amount"]['$gte'] = int(min_invs_connect)

        if max_invs_connect and max_invs_connect != "":
            query["Investing connections amount"]['$lte'] = int(max_invs_connect)
            
        # if profile_name and profile_name != "":
        #     query["Profile name"] = { "$regex": profile_name, "$options" :'i' }
            
        if new_profile_name and len(new_profile_name) > 0:
            query["Profile name"] = { "$in": new_profile_name }
            
        if firm and len(firm) > 0:
            #match any
            query["Firm"] = { "$in": firm }
        
        if sector_of_interest and len(sector_of_interest) > 0:
            #match any
            query["Investement sectors & tags"] = { "$in": sector_of_interest }

        #investment range filter
        min_investment = body.get("min_investment")
        max_investment = body.get("max_investment")
        
        if min_investment and min_investment != "" and max_investment and max_investment != "":
            query["Min investment"] = {}
            query["Min investment"]["$exists"] = True
            query["Max investment"] = {}
            query["Max investment"]["$exists"] = True

            query["Min investment"]['$gte'] = int(min_investment)
            query["Max investment"]['$gte'] = int(min_investment)

            query["Min investment"]['$lte'] = int(max_investment) 
            query["Max investment"]['$lte'] = int(max_investment) 

        
        # Counting Query Documents Vs. Total Documents
        query_count = SIGNAL_INVEST_DATA.count_documents(query)
        
        total_count = SIGNAL_INVEST_DATA.count_documents({})
        
        add_to_session("signal_total_count", total_count)

        if query_count < total_count:
          # add_to_session("signal_mongodb_query", query)
          current_user.update(set__filters__signal_back=json.dumps(query))

        else:
          # add_to_session("signal_mongodb_query", {})
          current_user.update(set__filters__signal_back=json.dumps({}))


        # Get Final Results Logic
        final_Results = str(request.args.get('finalResults',False))
        if final_Results == "true":
          final_query = json.loads(current_user.filters.get("twitter_back"))
          final_person_ids = TAIL_DATABASE.distinct("Signal person ID", final_query)
          final_person_ids = [int(i) for i in final_person_ids]
          query["Person id"] = { "$in": final_person_ids }
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


# Signal Count_Investors Route
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


# Signal Search Field Options Route
@app.route('/api/investors/signal/search', methods=["POST"])
@login_required
def search_signal_investors():
  try:
    body = request.get_json()
    field = body.get("field")
    query = body.get("query")
    limit = body.get("limit")
    result = SIGNAL_INVEST_DATA.distinct(field, { field: { "$regex": f'^{query}', "$options" :'i' } })#[:limit]
    result = [x for x in result if type(x) == str]
    return jsonify({
      "result" : result,
    })
  except:
    return jsonify({
      "result" : [],
    })

# Signal Get Filters Options
@app.route('/api/investors/signal/options')
@login_required
def signal_filter_options():
  try:
    try:
      stage_options = list(SIGNAL_INVEST_DATA.distinct("Sector & stage rankings"))
      stage_options = [x for x in stage_options if type(x) == str]
      position_options = list(SIGNAL_INVEST_DATA.distinct("Position"))
      position_options = [x for x in position_options if type(x) == str]
      new_profile_name_options = SIGNAL_INVEST_DATA.distinct("Profile name")
      new_profile_name_options = [x for x in new_profile_name_options if type(x) == str]
      firm_options = SIGNAL_INVEST_DATA.distinct("Firm")
      firm_options = [x for x in firm_options if type(x) == str]
      sector_of_interest_options = SIGNAL_INVEST_DATA.distinct("Investement sectors & tags")
      sector_of_interest_options = [x for x in sector_of_interest_options if type(x) == str]
    except:
      stage_options = [] 
      position_options = []
      new_profile_name_options = []
      firm_options = []
      sector_of_interest_options = []
    return jsonify({
      "options" : {
        "stage_options" : stage_options,
        "position_options" : position_options,
        "new_profile_name_options" : new_profile_name_options,
        "firm_options" : firm_options,
        "sector_of_interest_options" : sector_of_interest_options,
      }
    })
  except:
    return jsonify({
      "options" : {},
    })

## LinkedIn_Investors Routes
# LinkedIn Main Route
@app.route('/api/investors/linkedin', methods=["POST"])
@login_required
def handle_linkedin_investors():

    try:

        query = {}
        body = request.get_json() 
        
        # Save Query to Session
        # add_to_session("linkedin_query", body)
        current_user.update(set__filters__linkedin_front=body)
        

        # signal_mongodb_query = session["signal_mongodb_query"]
        signal_mongodb_query = json.loads(current_user.filters["signal_back"])


        # has_linkedin_query = {"$and":[{"Linkedin Profile Attached": {"$ne": None}}, {"Linkedin Profile Attached": {"$ne": ""}}]}
        # has_linkedin_query = {}

        # person_ids_list = SIGNAL_INVEST_DATA.distinct("Person id", {**signal_mongodb_query, **has_linkedin_query})
        person_ids_list = SIGNAL_INVEST_DATA.distinct("Person id", signal_mongodb_query)

        # if signal_mongodb_query != {}:
        query["Person id"] = { "$in": person_ids_list }
        # else:
        #   query = {**has_linkedin_query}

        # has_linkedin_count = len(person_ids_list)

        signal_query_count = SIGNAL_INVEST_DATA.count_documents(signal_mongodb_query)        
      
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

        no_linkedin_count = signal_query_count - query_count

        print("Slow Part 2 --- %s seconds ---" % (time.time() - start_time_2))
        total_count = signal_query_count
    
        current_user.update(set__filters__linkedin_back=json.dumps(query))

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
            # "has_linkedin_count": has_linkedin_count,
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


# LinkedIn Count_Investors Route
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

# LinkedIn Get Filters Options
@app.route('/api/investors/linkedin/options')
@login_required
def linkedin_filter_options():
  try:
    try:
      stage_options = list(LINKEDIN_INVEST_DATA.distinct("Sector & stage rankings"))
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


## Twitter_Investors Routes
# Twitter Main Route
@app.route('/api/investors/twitter', methods=["POST"])
@login_required
def handle_twitter_investors():

    try:
        start_time = time.time()

        query = {}
        
        body = request.get_json() 
        
        # Save Query to Session
        current_user.update(set__filters__twitter_front=body)
        

        signal_mongodb_query = json.loads(current_user.filters["signal_back"])

        person_ids_list = SIGNAL_INVEST_DATA.distinct("Person id", signal_mongodb_query)  #SLOW STEP
        print("here:", time.time()-start_time)
        # Converting to str() because person_id is stored as strings in twitter database
        person_ids_list = [str(i) for i in person_ids_list]


        query["Signal person ID"] = { "$in": person_ids_list }
       
        signal_query_count = SIGNAL_INVEST_DATA.count_documents(signal_mongodb_query)        
              
        # Counting Query Documents Vs. Total Documents
        query_count = TWITTER_INVEST_DATA.count_documents(query)
        no_twitter_count = signal_query_count - query_count
        total_count = TWITTER_INVEST_DATA.count_documents({})


        ## ADDING TO QUERY ##

        # Confidence Query Logic
        confidence = body.get("confidence")
        if confidence and len(confidence) > 0:
            #match any
            query["Confidence"] = { "$in": confidence }
        
        # Followers Query Logic
        min_followers = body.get("min_followers")
        max_followers = body.get("max_followers")
        
        if (min_followers and min_followers != "") or (max_followers and max_followers != ""):
            query["Followers"] = {}
            query["Followers"]["$exists"] = True

        if min_followers and min_followers != "":
            query["Followers"]['$gte'] = int(min_followers)

        if max_followers and max_followers != "":
            query["Followers"]['$lte'] = int(max_followers) 
              
        # Following Query Logic
        min_following = body.get("min_following")
        max_following = body.get("max_following")
        
        if (min_following and min_following != "") or (max_following and max_following != ""):
            query["Following"] = {}
            query["Following"]["$exists"] = True

        if min_following and min_following != "":
            query["Following"]['$gte'] = int(min_following)

        if max_following and max_following != "":
            query["Following"]['$lte'] = int(max_following) 

        #Logic for pagination
        offset = int(request.args.get('offset',0))
        limit = 10

        starting_id = TWITTER_INVEST_DATA.find(query).sort('_id', pymongo.ASCENDING)

        try:
          last_id = starting_id[offset]['_id']
        except:
          last_id = None
 

        current_user.update(set__filters__twitter_back=json.dumps(query))

        next_chunk = offset + limit
        prev_chunk = 0
        if offset - limit > 0:
            prev_chunk = offset - limit


        if last_id:
          json_data = TWITTER_INVEST_DATA.find({**query, **{"_id": {'$gte': last_id}}}, limit=limit).sort('_id', pymongo.ASCENDING)
        else:
          json_data = []        
            
        query_count = TWITTER_INVEST_DATA.count_documents(query)

        return jsonify({
            "investors": loads(dumps(json_data)),
            "total_count": total_count,
            "query_count": query_count,
            "limit": limit,
            "next_chunk": next_chunk,
            "prev_chunk": prev_chunk,
            "no_twitter_count": no_twitter_count,
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
            "no_twitter_count": 0,
        })


# Twitter Count_Investors Route
@app.route('/api/investors/twitter/count', methods=["POST"])
@login_required
def count_twitter_investors():
  try:
    body = request.get_json()
    field = body.get("field")
    query = body.get("query")
    count = TWITTER_INVEST_DATA.count_documents({ field: { "$regex": query, "$options" :'i' } })
    return jsonify({
      "count" : count,
    })
  except:
    return jsonify({
      "count" : 0,
    })

# Twitter Get Filters Options
@app.route('/api/investors/twitter/options')
@login_required
def twitter_filter_options():
  try:
    try:
      confidence_options = TWITTER_INVEST_DATA.distinct("Confidence",{"Confidence":{"$nin":["",None,float("nan")]}})
    except:
      confidence_options = []
    return jsonify({
      "options" : {
        "confidence_options" : confidence_options,
      }
    })
  except:
    return jsonify({
      "options" : {},
    })


## Angelist_Investors Routes
# Angelist Main Route
@app.route('/api/investors/angelist', methods=["POST"])
@login_required
def handle_angelist_investors():

    try:
        start_time = time.time()

        query = {}
        
        body = request.get_json() 
        
        # Save Query to Session
        current_user.update(set__filters__angelist_front=body)
        

        twitter_mongodb_query = json.loads(current_user.filters["twitter_back"])

        person_ids_list = TWITTER_INVEST_DATA.distinct("Signal person ID", twitter_mongodb_query)  #SLOW STEP
        print("here:", time.time()-start_time)
        # Converting to int() because person_id is stored as strings in twitter database
        person_ids_list = [int(i) for i in person_ids_list]


        query["Signal person ID"] = { "$in": person_ids_list }
       
        twitter_query_count = TWITTER_INVEST_DATA.count_documents(twitter_mongodb_query)        
              
        # Counting Query Documents Vs. Total Documents
        query_count = ANGELIST_INVEST_DATA.count_documents(query)
        no_angelist_count = twitter_query_count - query_count
        total_count = ANGELIST_INVEST_DATA.count_documents({})


        ## ADDING TO QUERY ##
       
        # Education Amount Query Logic
        min_education_amount = body.get("min_education_amount")
        max_education_amount = body.get("max_education_amount")
        
        if (min_education_amount and min_education_amount != "") or (max_education_amount and max_education_amount != ""):
            query["Education Amount"] = {}
            query["Education Amount"]["$exists"] = True

        if min_education_amount and min_education_amount != "":
            query["Education Amount"]['$gte'] = int(min_education_amount)

        if max_education_amount and max_education_amount != "":
            query["Education Amount"]['$lte'] = int(max_education_amount) 
              

        #Logic for pagination
        offset = int(request.args.get('offset',0))
        limit = 10

        starting_id = ANGELIST_INVEST_DATA.find(query).sort('_id', pymongo.ASCENDING)

        try:
          last_id = starting_id[offset]['_id']
        except:
          last_id = None
 

        current_user.update(set__filters__angelist_back=json.dumps(query))

        next_chunk = offset + limit
        prev_chunk = 0
        if offset - limit > 0:
            prev_chunk = offset - limit


        if last_id:
          json_data = ANGELIST_INVEST_DATA.find({**query, **{"_id": {'$gte': last_id}}}, limit=limit).sort('_id', pymongo.ASCENDING)
        else:
          json_data = []        
            
        query_count = ANGELIST_INVEST_DATA.count_documents(query)

        return jsonify({
            "investors": loads(dumps(json_data)),
            "total_count": total_count,
            "query_count": query_count,
            "limit": limit,
            "next_chunk": next_chunk,
            "prev_chunk": prev_chunk,
            "no_angelist_count": no_angelist_count,
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
            "no_angelist_count": 0,
        })


# angelist Count_Investors Route
@app.route('/api/investors/angelist/count', methods=["POST"])
@login_required
def count_angelist_investors():
  try:
    body = request.get_json()
    field = body.get("field")
    query = body.get("query")
    count = ANGELIST_INVEST_DATA.count_documents({ field: { "$regex": query, "$options" :'i' } })
    return jsonify({
      "count" : count,
    })
  except:
    return jsonify({
      "count" : 0,
    })

# angelist Get Filters Options
@app.route('/api/investors/angelist/options')
@login_required
def angelist_filter_options():
  try:
    # try:
    #   confidence_options = ANGELIST_INVEST_DATA.distinct("Confidence",{"Confidence":{"$nin":["",None,float("nan")]}})
    # except:
    #   confidence_options = []
    return jsonify({
      "options" : {
        # "confidence_options" : confidence_options,
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
 
