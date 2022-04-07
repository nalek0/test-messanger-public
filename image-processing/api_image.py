import re

from flask import Blueprint, request, make_response
from PIL import Image
from io import BytesIO
import base64

from database import ImageTable, db

image_api = Blueprint("api", __name__,
                      url_prefix="/image")


@image_api.route("/get/<int:image_id>/<int:size>")
def get_image(image_id: int, size: int):
    result_size = ImageTable.sizes[0]
    for sz in ImageTable.sizes[1:]:
        if abs(sz - size) < abs(result_size - size):
            result_size = sz

    table = ImageTable.query.get_or_404(image_id)
    img_byte_arr = BytesIO()
    image = table.get_image(result_size)
    image.save(img_byte_arr, format="JPEG")

    response = make_response(img_byte_arr.getvalue())
    response.headers.set('Content-Type', 'image/jpeg')
    return response


@image_api.route("/add", methods=["POST"])
def add_image():
    image_data = re.sub('^data:image/.+;base64,', '', request.json['image'])
    image = Image.open(BytesIO(base64.b64decode(image_data)))
    table = ImageTable()
    for size in ImageTable.sizes:
        image.thumbnail((size, size))
        table.set_image(size, image)
    db.session.add(table)
    db.session.commit()
    return "OK"
