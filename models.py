from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), nullable=False)  # 作者欄位
    content = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Recipe {self.title}>"

