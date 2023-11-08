from flask import Blueprint, request, render_template, abort, jsonify
from werkzeug.utils import secure_filename
from cache import redis
import json
import os
from models import UserFavorite, User, Business
from db import db
from sqlalchemy.orm import aliased
from api.schema import UserSchema, BusinessSchema
import pickle

api_blueprint = Blueprint('api_blueprint', __name__ )

@api_blueprint.route("/test")
def test():
    redis.incr('hits')
    hits = redis.get('hits')
    return hits

@api_blueprint.route('/user/<user_id>/favorites')
def favorite_business(user_id):
    if not redis.exists('user:id:%s'%(user_id)):
        user = db.session.query(User).where(User.id == user_id).first()
        user = UserSchema().dump(user)
        redis.set('user:id:%s'%(user_id), json.dumps(user))
        ##TTL setting
        redis.expire('user:id:%s'%(user_id), time=60)
        print("User FROM DB")
    else:
        print("User from Cache")
        user = json.loads(redis.get('user:id:%s'%(user_id)))
    
    n,l = redis.scan(cursor=0,match="favorites:user:id:%s:business_id:*"%(user_id))
    if len(l)<=0:
        favorites = db.session.query(Business).join(UserFavorite, onclause=Business.business_id == UserFavorite.business_id).where(UserFavorite.user_id == user_id).all()
        favorites_list = BusinessSchema().dump(favorites,many=True)
        for i in favorites_list:
            redis.set("favorites:user:id:%s:business_id:%s"%(user_id, i['business_id']), pickle.dumps(i))
            redis.expire("favorites:user:id:%s:business_id:%s", time=60)
        print("FAVORITES FROM DB")
    else:
        (n,arr) = redis.scan(0,"favorites:user:id:%s:business_id:*"%(user_id),1000)
        favorites_list = []
        print(arr)
        for i in arr:
            print(i)
            favorites_list.append(pickle.loads(redis.get(i)))
        print("FAVORITES FROM CACHE")

    return jsonify({
        "user": user,
        "favorites": favorites_list
    })  