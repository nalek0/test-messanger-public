import base64
from io import BytesIO
from typing import Tuple

from PIL import Image
from flask import url_for
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ImageTable(db.Model):
    """
    Class, that saves image thumbnails with its metadata
    """
    sizes = [512, 128, 32]

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)

    image512 = db.Column(db.LargeBinary, nullable=False)
    image512_width = db.Column(db.Integer, nullable=False)
    image512_height = db.Column(db.Integer, nullable=False)

    image128 = db.Column(db.LargeBinary, nullable=False)
    image128_width = db.Column(db.Integer, nullable=False)
    image128_height = db.Column(db.Integer, nullable=False)

    image32 = db.Column(db.LargeBinary, nullable=False)
    image32_width = db.Column(db.Integer, nullable=False)
    image32_height = db.Column(db.Integer, nullable=False)

    def set_image(self, size: int, image: Image) -> None:
        """
        Saves image as thumbnail with given size

        :param size: image size (must be an integer from ImageTable.sizes array)
        :param image: PIL Image
        :return: None
        """
        setattr(self, f"image{size}", image.tobytes())
        setattr(self, f"image{size}_width", image.width)
        setattr(self, f"image{size}_height", image.height)

    def get_size(self, size: int) -> Tuple[int, int]:
        """
        Util to get required thumbnail size tuple

        :param size: size of the thumbnail
        :return: size as tuple of two ints
        """
        return getattr(self, f"image{size}_width"), getattr(self, f"image{size}_height")

    def get_image(self, size: int) -> Image:
        """
        :param size: size of the thumbnail
        :return: PIL Image object
        """
        return Image.frombytes(mode="RGBA",
                               size=(self.get_size(size)),
                               data=getattr(self, f"image{size}"))

    def get_image_byteio(self, size: int) -> BytesIO:
        """
        :param size: size of the thumbnail
        :return: byte stream
        """
        img_byte_arr = BytesIO()
        image = self.get_image(size)
        image.save(img_byte_arr, format="PNG")
        return img_byte_arr

    def load(self, base64_code: str):
        """
        Updates object so that now it saves thumbnails for image with given base64 code
        :param base64_code: image code
        :return: self object
        """
        image = Image.open(BytesIO(base64.b64decode(base64_code)))
        image = image.convert(mode="RGBA")
        for size in ImageTable.sizes:
            image.thumbnail((size, size))
            self.set_image(size, image)
        return self

    def get_thumbnail_json(self, size: int) -> dict:
        return {
            "url": url_for("api.image_api.get_image", image_id=self.id, size=size, _external=True)
        }

    def json(self) -> dict:
        thumbnails = {}
        for sz in self.sizes:
            thumbnails[str(sz)] = self.get_thumbnail_json(sz)
        return {
            "id": self.id,
            "thumbnails": thumbnails
        }
