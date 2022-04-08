import math
import re

from flask import Blueprint, request, make_response

from database import ImageTable, db

image_api = Blueprint("image_api", __name__,
                      url_prefix="/image")


@image_api.route("/get/<int:image_id>/<int:size>")
def get_image(image_id: int, size: int):
    result_size = math.inf
    for sz in ImageTable.sizes:
        if abs(sz - size) < abs(result_size - size):
            result_size = sz

    table: ImageTable = ImageTable.query.get_or_404(image_id)

    image_response_data = table.get_image_byteio(result_size).getvalue()
    response = make_response(image_response_data)
    response.headers.set('Content-Type', 'image/png')
    return response


@image_api.route("/get/data/<int:image_id>")
def get_image_data(image_id: int):
    return ImageTable.query.get_or_404(image_id).json()


@image_api.route("/add", methods=["POST"])
def add_image():
    base64_code = re.sub('^data:image/.+;base64,', '', request.json['image'])
    image_table = ImageTable().load(base64_code)
    db.session.add(image_table)
    db.session.commit()
    return image_table.json()
