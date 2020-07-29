from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
import random
import hashlib

app = Flask(__name__)
api = Api(app)


SCREEN_COUNT = 5
SEAT_LIMIT = 100
reservation_no = 0

USERNAME = "admin"
PASSWORD = "admin"
PASSWORD_HASH = hashlib.sha256(PASSWORD.encode()).hexdigest()

movies = []
reservations = []
reservations_nums = 0


class Movies(Resource):
    def get(self):
        return movies, 200

    def post(self):  # admin only
        content = request.get_json()
        if (content["user"] == USERNAME and content["password"] == hashlib.sha256(PASSWORD.encode()).hexdigest()):
            content = request.get_json()
            for screen_no in range(SCREEN_COUNT):
                content["screen_no"] = screen_no
                if content not in movies:
                    movies.append(content)
                    return {"screen_no": screen_no}, 201
            return None, 404
        else:
            return None, 401


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


class Ticket(Resource):
    def post(self):
        content = request.get_json()
        if "screen_no" in content:
            for movie in movies:
                if movie == content:
                    # only admins are allowed
                    res_count = 0
                    for res in reservations:
                        if res["movie"] == movie:
                            res_count += 1
                    if res_count > 99:
                        return None, 409
                    reservation_no = str(len(reservations) + 1)
                    reservations.append(
                        {
                            "movie": content,
                            "reservation_no": reservation_no,
                            "seat_no": res_count + 1,
                        }
                    )
                    return {"reservation_no": reservation_no}, 201
            return None, 404

    def get(self):
        content = request.get_json()
        if 'reservation_no' not in content:
            if (content["user"] == USERNAME and content["password"] == hashlib.sha256(PASSWORD.encode()).hexdigest()):
                res_temp = []
                for r in reservations:
                    ticket = r["movie"]
                    ticket["seat_no"] = r["seat_no"]
                    ticket["reservation_no"] = r["reservation_no"]
                    res_temp.append(ticket)
                return res_temp, 200
            else:
                return None, 401
        else:
            for res in reservations:
                if res["reservation_no"] == content["reservation_no"]:
                    ticket = res["movie"]
                    ticket["seat_no"] = res["seat_no"]
                    print(ticket)
                    return ticket, 200

            return None, 404

    def put(self):
        content = request.get_json()
        res_no = content["reservation_no"]
        seat_no = content["seat_no"]

        for reservation in reservations:
            if reservation["reservation_no"] == res_no:
                tmp = reservation.copy()
                tmp["seat_no"] = seat_no
                if tmp not in reservations:
                    reservation["seat_no"] = seat_no
                    return None, 200
                else:
                    return None, 409
        return None, 404

    def delete(self):
        res_no = request.get_json()["reservation_no"]
        for reservation in reservations:
            if res_no == reservation["reservation_no"]:
                reservations.remove(reservation)
                return None, 200
        return None, 404


api.add_resource(Movies, "/movies")
api.add_resource(MoviesNameDate, "/movies/<name>/<date>")
api.add_resource(Ticket, "/ticket")

if __name__ == "__main__":
    app.run(debug=True)
