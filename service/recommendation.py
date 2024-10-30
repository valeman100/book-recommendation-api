from flask import Blueprint, jsonify, request
import requests
from flask_login import login_required, current_user

service_bp = Blueprint('recommendation', __name__, url_prefix='/service')


@service_bp.route("/get-recommendation", methods=["POST"])
@login_required
def get_recommendation():
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No image provided"}), 400

    files = {'image': file.read()}  # Read the file's bytes
    api_url = f"http://localhost:3000/my-bookshelf/get-recommendation/{current_user.id}"

    try:
        response = requests.post(api_url, files=files)
        response.raise_for_status()
        result = response.json()  # Parse the JSON response
        return jsonify(result)  # Return the result to the front-end
    except requests.exceptions.RequestException as e:
        print(f"Error calling external API: {e}")
        return jsonify({"error": "Failed to call API"}), 500
