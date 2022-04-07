from typing import Tuple

from PIL import Image
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ImageTable(db.Model):
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
        setattr(self, f"image{size}", image.tobytes())
        setattr(self, f"image{size}_width", image.width)
        setattr(self, f"image{size}_height", image.height)

    def get_size(self, size: int) -> Tuple[int, int]:
        return getattr(self, f"image{size}_width"), getattr(self, f"image{size}_height")

    def get_image(self, size) -> Image:
        return Image.frombytes(mode="RGB",
                               size=(self.get_size(size)),
                               data=getattr(self, f"image{size}"))
