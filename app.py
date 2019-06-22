from sqlalchemy.pool import SingletonThreadPool
from models import Base, User, Food, Recipe, Recipe_Food, Favorite
from flask import Flask, request, jsonify, url_for, abort, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import itertools
from operator import itemgetter
from collections import OrderedDict
from apriori import Apriori

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

engine = create_engine('mysql+pymysql://{your-username}:{your-password}@{your-ip:port}/{your-database}')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

# 0
# AUTHENTICATION AND AUTHORIZATION
# -------------------------------------------------------------------------------------------


@auth.verify_password
def verify_password(mail, password):
    user = session.query(User).filter_by(mail=mail).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True
# -------------------------------------------------------------------------------------------

# 1
# USER PART
# -------------------------------------------------------------------------------------------


@app.route("/api/v1/users", methods=['POST'])
def new_user():
    session.rollback()
    name = request.json.get('name')
    mail = request.json.get('mail')
    password = request.json.get('password')
    if name is None or mail is None or password is None:
        abort(400)  # missing arguments
    if session.query(User).filter_by(mail=mail).first() is not None:
        abort(400)  # existing user
    user = User(name=name, mail=mail)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({'user': user.serialize}), 201


@app.route("/api/v1/users", methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def users():
    session.rollback()
    if request.method == 'GET':
        users = session.query(User).all()
        return jsonify(users=[user.serialize for user in users]), 200
    elif request.method == 'PUT':
        name = request.json.get('name')
        mail = request.json.get('mail')
        password = request.json.get('password')
        if name is None and mail is None and password is None:
            abort(400)  # No argument
        if name:
            g.user.name = name
        if mail:
            g.user.mail = mail
        if password:
            g.user.hash_password(password)
        session.add(g.user)
        session.commit()
        return jsonify({'updated_user': g.user.serialize}), 202
    elif request.method == 'DELETE':
        session.delete(g.user)
        session.commit()
        return jsonify({'deleted_user': g.user.serialize}), 202


@app.route("/api/v1/users/<string:mail>")
@auth.login_required
def user_by_mail(mail):
    user = session.query(User).filter_by(mail=mail).one()
    if not user:
        abort(400)
    return jsonify(user.serialize), 200
# -------------------------------------------------------------------------------------------


# 2
# FOOD PART
# -------------------------------------------------------------------------------------------
@app.route("/api/v1/foods", methods=['GET', 'POST', 'DELETE'])
@auth.login_required
def foods():
    if request.method == 'POST':
        session.rollback()
        foods = list()
        json_array = request.get_json()
        for json_item in json_array['Foods']:
            name = json_item['name']
            image = json_item['image']
            calorie = json_item['calorie']
            carb = json_item['carb']
            protein = json_item['protein']
            fat = json_item['fat']
            health_point = json_item['health_point']
            category = json_item['category']
            description = json_item['description']
            food = Food(name=name, image=image, calorie=calorie, carb=carb,
                        protein=protein, fat=fat, health_point=health_point, category=category, description=description)
            session.add(food)
            foods.append(food)
            session.commit()
        return jsonify([food.serialize for food in foods]), 201
    elif request.method == 'DELETE':
        session.rollback()
        foods = session.query(Food).all()
        for food in foods:
            session.delete(food)
            session.commit()
        return jsonify([food.serialize for food in foods]), 202
    elif request.method == 'GET':
        session.rollback()
        foods = session.query(Food).all()
        return jsonify([food.serialize for food in foods]), 200


# @app.route("/api/v1/foods/<string:name>", methods=['DELETE'])
# def delete_food_by_name(name):
#     session.rollback()
#     food = session.query(Food).filter_by(name=name).one()
#     session.delete(food)
#     session.commit()
#     return jsonify(food.serialize), 202


# @app.route("/api/v1/foods")
# # @auth.login_required
# def foods():
#     session.rollback()
#     foods = session.query(Food).all()
#     return jsonify([food.serialize for food in foods]), 200


# @app.route("/api/v1/foods/<string:name>")
# # @auth.login_required
# def food_by_name(name):
#     food = session.query(Food).filter_by(name=name).one()
#     if not food:
#         abort(400)
#     return jsonify(food.serialize), 200
# -------------------------------------------------------------------------------------------


# 3
# RECIPE PART
# -------------------------------------------------------------------------------------------
@app.route("/api/v1/recipes", methods=['GET', 'POST', 'DELETE'])
@auth.login_required
def recipes():
    session.rollback()
    if request.method == 'POST':
        recipes = list()
        json_array = request.get_json()
        for json_item in json_array['Recipes']:
            name = json_item['name']
            image = json_item['image']
            rating = json_item['rating']
            calorie = json_item['calorie']
            carb = json_item['carb']
            protein = json_item['protein']
            fat = json_item['fat']
            cooking_minutes = json_item['cooking_minutes']
            description = json_item['description']
            user_mail = json_item['user_mail']
            recipe = Recipe(name=name, image=image, rating=rating, calorie=calorie, carb=carb,
                            protein=protein, fat=fat, cooking_minutes=cooking_minutes,
                            description=description, user_mail=user_mail)
            session.add(recipe)
            recipes.append(recipe)
            session.commit()
        return jsonify([recipe.serialize for recipe in recipes]), 201
    elif request.method == 'DELETE':
        recipes = session.query(Recipe).all()
        for recipe in recipes:
            session.delete(recipe)
            session.commit()
        return jsonify([recipe.serialize for recipe in recipes]), 202
    elif request.method == 'GET':
        recipes = session.query(Recipe).all()
        return jsonify([recipe.serialize for recipe in recipes]), 200

# @app.route("/api/v1/recipes", methods=['GET'])
# # @auth.login_required
# def recipes():
#     recipes = session.query(Recipe).all()
#     return jsonify([recipe.serialize for recipe in recipes]), 200


# @app.route("/api/v1/recipes/<int:id>")
# # @auth.login_required
# def recipe_by_id(id):
#     recipe = session.query(Recipe).filter_by(id=id).one()
#     if not recipe:
#         abort(400)
#     return jsonify(recipe.serialize), 200
# -------------------------------------------------------------------------------------------


# 4
# RECIPE_FOOD PART
# -------------------------------------------------------------------------------------------
@app.route("/api/v1/recipe_food_add", methods=['POST', 'DELETE'])
@auth.login_required
def recipe_foods():
    if request.method == 'POST':
        session.rollback()
        json_array = request.get_json()
        ingredients = list()
        for json_item in json_array:
            recipe_id = json_item['recipe_id']
            # array = request.get_json()
            for item in json_item['Recipe_Ingredients']:
                food_name = item['food_name']
                recipe_food = Recipe_Food(
                    food_name=food_name, recipe_id=recipe_id)
                ingredients.append(recipe_food)
                session.add(recipe_food)
                session.commit()
        return jsonify([ingredient.serialize for ingredient in ingredients]), 201
    elif request.method == 'DELETE':
        session.rollback()
        recipe_foods = session.query(Recipe_Food).all()
        for recipe_food in recipe_foods:
            session.delete(recipe_food)
            session.commit()
        return jsonify([recipe_food.serialize for recipe_food in recipe_foods]), 202


@app.route("/api/v1/recipe_food/<int:recipe_id>")
@auth.login_required
def recipe_food(recipe_id):
    recipe_foods = session.query(Food).filter(
        (Recipe_Food.food_name == Food.name) & (Recipe_Food.recipe_id == recipe_id)).all()
    return jsonify([recipe_food.serialize for recipe_food in recipe_foods]), 200


def contains(array, item):
    array = set(array)
    # print(array)
    # print(item)
    i = 0
    for a in array:
        # print(a , item)
        if a == item:
            return True
        # if(i == len(array)):
        #     break
        # i += 1
    return False


@app.route("/api/v1/recipe_food", methods=['POST'])
@auth.login_required
def recipe_advices():
    json_array = request.get_json()
    ingredient_names = list()
    for json_item in json_array:
        ingredient_names.append(json_item['name'])

    recipes = session.query(Recipe_Food).filter(
        Recipe_Food.food_name.in_(ingredient_names)).all()
    recipe_ids = set()

    for recipe in recipes:
        recipe_ids.add(recipe.recipe_id)

    arr = list()
    for id in recipe_ids:
        arr.append(id)
        arr.append(0)

    i = 0
    while i < len(arr):
        if i % 2 == 0:
            ingredients = session.query(
                Recipe_Food).filter_by(recipe_id=arr[i])
            for ingredient in ingredients:
                if contains(ingredient_names, ingredient.food_name):
                    arr[i + 1] += 1
        i += 1

    d = dict(itertools.zip_longest(*[iter(arr)] * 2, fillvalue=0))
    s = OrderedDict(sorted(d.items(), key=itemgetter(1), reverse=True))

    print(type(s))

    result = list()
    for key, value in s.items():
        result.append(key)

    for res in result:
        print(res)

    advice_recipes = list()
    for res in result:
        advice_recipes.append(session.query(Recipe).filter_by(id=res).first())

    return jsonify([advice_recipe.serialize for advice_recipe in advice_recipes]), 200
# -------------------------------------------------------------------------------------------

# 5
# FAVORITES PART
# -------------------------------------------------------------------------------------------

fs = list()
@app.route("/api/v1/favorites", methods=['POST', 'GET', 'DELETE'])
@auth.login_required
def favorites():
    if request.method == 'POST':
        session.rollback()
        # session.flush()
        favorites = session.query(Favorite).filter_by(
            user_mail=g.user.mail).all()
        for favorite in favorites:
            session.delete(favorite)
            session.commit()
        favorites = list()
        user_mail = g.user.mail
        print(request.data)
        json_array = request.get_json()
        for json_item in json_array:
            print(json_item)
            recipe_id = json_item
            favorite = Favorite(user_mail=user_mail, recipe_id=recipe_id)
            favorites.append(favorite)
            session.add(favorite)
            session.commit()
        # return jsonify([favorite.serialize for favorite in favorites]), 201
        global fs
        fs = session.query(Favorite).filter_by(user_mail=g.user.mail).all()
        return request.data
    elif request.method == 'GET':
        session.rollback()
        favorites = session.query(Favorite).filter_by(
            user_mail=g.user.mail).all()

        recipe_ids = list()
        for favorite in favorites:
            recipe_ids.append(favorite.recipe_id)
        print(recipe_ids)
        recipes = session.query(Recipe).filter(
            Recipe.id.in_(str(recipe_ids))).all()
        return jsonify([recipe.serialize for recipe in recipes]), 201
    elif request.method == 'DELETE':
        session.rollback()
        favorites = session.query(Favorite).filter_by(
            user_mail=g.user.mail).all()
        for favorite in favorites:
            session.delete(favorite)
            session.commit()
        return jsonify([favorite.serialize for favorite in favorites]), 202


# @app.route("/api/v1/recipe_food/<int:recipe_id>")
# @auth.login_required
# def recipe_food(recipe_id):
#     recipe_foods = session.query(Food).filter(
#         (Recipe_Food.food_name == Food.name) & (Recipe_Food.recipe_id == recipe_id)).all()
#     return jsonify([recipe_food.serialize for recipe_food in recipe_foods]), 200


# @app.route("/api/v1/recipe_food")
# @auth.login_required
# def recipe_advices():
#     recipe_ids = session.query(Recipe_Food.recipe_id).filter(
#         Recipe_Food.food_name.in_(["Portakal", "Bitter Çikolata"])).distinct().all()
#     advice_recipes = session.query(Recipe).filter(
#         Recipe.id.in_(str(recipe_ids))).all()

#     return jsonify([advice_recipe.serialize for advice_recipe in advice_recipes]), 200
# -------------------------------------------------------------------------------------------

# 6
# APIRIORI PART
# -------------------------------------------------------------------------------------------
@app.route("/api/v1/apriori")
@auth.login_required
def apriori():
    session.rollback()
    users = session.query(User).all()

    favs = list()
    for user in users:
        favIds = list()
        favorites = session.query(Favorite).filter_by(
            user_mail=user.mail).all()
        for favorite in favorites:
            favIds.append(str(favorite.recipe_id))
        favs.append(favIds)

    minsup = 0.4
    minconf = 0.4

    apriori = Apriori(favs, minsup, minconf)
    apriori.run()
    apriori.print_frequent_itemset()
    result = apriori.print_rule()

    # print(result)

    apriori_advices = list()

    for res in result:
        x = res.split(' ==> ')
        # print(len(x[0]))
        if len(x[0]) <= 2:
            # print(x[0])
            apriori_advices.append(x[0])
            apriori_advices.append(x[1])

    # print(apriori_advices)

    key = list()
    value = list()

    i = 0
    while i < len(apriori_advices):
        key.append(int(apriori_advices[i]))
        value.append(int(apriori_advices[i + 1]))
        i += 4

    favorites = session.query(Favorite).filter_by(user_mail=g.user.mail).all()
    print(favorites)
    favoriteIds = list()
    for favorite in favorites:
        favoriteIds.append(favorite.recipe_id)

    print(favoriteIds)
    print(key)
    adviceIds = list()
    i = 0
    if(len(favoriteIds) > 0):
        while i < len(key):
            if contains(fs, key[i]) != True:
                adviceIds.append(value[i])
            i += 1

    print(adviceIds)
    adviceIds = list(set(adviceIds))
    print(adviceIds)
    advices = session.query(Recipe).filter(Recipe.id.in_(adviceIds)).all()

    return jsonify([advice.serialize for advice in advices]), 201
# -------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.debug = True
    # app.env = "development"
    app.run(host='0.0.0.0', port=5000)
