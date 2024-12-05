from datetime import datetime
import pytz
from flask_sqlalchemy import SQLAlchemy

# 台灣時區
taiwan_tz = pytz.timezone('Asia/Taipei')
def get_current_time():
    return datetime.now(taiwan_tz)

db = SQLAlchemy()

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), nullable=False)  # 作者欄位
    content = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100), nullable=True)  # 新增欄位用於存儲圖片文件名
    difficulty = db.Column(db.String(1), nullable=False)  # 儲存難度星級
    created_at = db.Column(db.DateTime, default=get_current_time)  # 新增時的時間
    category = db.Column(db.String(50), nullable=True)   # 新增類別欄位

    def __repr__(self):
        return f"<Recipe {self.title}>"

