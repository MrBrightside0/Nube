from flask import Blueprint,jsonify  

api_bp = Blueprint("api",__name__)

@api_bp.route("/get-air-quality")
def get_air_quality():
    data = {}
    return jsonify(data)
