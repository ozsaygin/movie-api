from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
import random

app = Flask(__name__)
api = Api(app)


SCREEN_COUNT = 5
SEAT_LIMIT = 100
reservation_no = 0

USERNAME = 'admin'
PASSWORD = 'admin'

movies = []
reservations = []
reservations_nums = 0
parser = reqparse.RequestParser()


class Movies(Resource):
    def get(self):
        print(request.get_json())
        return movies, 200

    def post(self): # admin only
        movie = request.get_json()
        for i in range(SCREEN_COUNT):
            tmp = movie
            tmp["screen_no"] = i
            if tmp not in movies:
                movies.append(tmp)
                return {"screen_no": i}, 201

        return None, 404


class MoviesNameDate(Resource):
    def get(self, name, date):
        movie_list = []
        for movie in movies:
            if movie["name"] == name and movie["date"] == date:
                movie_list.append(movie)

        if movie_list != []:
            return movie_list, 200
        else:
            return None, 404

    def delete(self, name, date):
        for movie in movies:
            if movie["name"] == name and movie["date"] == date:
                movies.remove(movie)
                return None, 200
        return None, 404


# class Ticket(Resource):
#     def post(self):
#         movie = request.get_json()
#         if movie in movies: # session exists
#             if movie in reservations: # session
#                 if len(movie['tickets']) <= 100:
                    
#         else: # session does not exist
#             return None, 404


    # def get(self):
    #     data = request.get_json()
    #     res_no = data['reservation_no']

#     def put(self):
#         pass

#     def delete(self):
#         pass


api.add_resource(Movies, "/movies")
api.add_resource(MoviesNameDate, "/movies/<name>/<date>")
# api.add_resource(Ticket, "/ticket")

if __name__ == "__main__":
    app.run(debug=True)
