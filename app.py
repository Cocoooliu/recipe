from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError  # 用於捕獲數據庫操作中的錯誤

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # 設定 secret key 以啟用 flash 消息
db = SQLAlchemy(app)
api = Api(app)

# 食譜資料庫模型
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Recipe {self.title}>"

# 初始化資料庫
with app.app_context():
    db.create_all()

# RESTful API 類別
class RecipeResource(Resource):
    def get(self, recipe_id=None):
        if recipe_id:
            recipe = Recipe.query.get_or_404(recipe_id)
            return jsonify({
                'id': recipe.id,
                'title': recipe.title,
                'author': recipe.author,
                'content': recipe.content,
                'steps': recipe.steps
            })
        else:
            recipes = Recipe.query.all()
            return jsonify([{
                'id': recipe.id,
                'title': recipe.title,
                'author': recipe.author,
                'content': recipe.content,
                'steps': recipe.steps
            } for recipe in recipes])

    def post(self):
        data = request.get_json()
        new_recipe = Recipe(
            title=data['title'],
            author=data['author'],
            content=data['content'],
            steps=data['steps']
        )
        db.session.add(new_recipe)
        db.session.commit()
        return jsonify({'message': 'Recipe created successfully!'}), 201

    def put(self, recipe_id):
        data = request.get_json()
        recipe = Recipe.query.get_or_404(recipe_id)
        recipe.title = data['title']
        recipe.author = data['author']
        recipe.content = data['content']
        recipe.steps = data['steps']
        db.session.commit()
        return jsonify({'message': 'Recipe updated successfully!'})

    def delete(self, recipe_id):
        recipe = Recipe.query.get_or_404(recipe_id)
        db.session.delete(recipe)
        db.session.commit()
        return jsonify({'message': 'Recipe deleted successfully!'})

# 註冊 API 路由
api.add_resource(RecipeResource, '/api/recipes', '/api/recipes/<int:recipe_id>')

# 前端頁面
@app.route('/')
def index():
    recipes = Recipe.query.all()
    return render_template('index.html', recipes=recipes)

@app.route('/recipe/<int:recipe_id>')
def show_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe.html', recipe=recipe)

@app.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if request.method == 'POST':
        recipe.title = request.form['title']
        recipe.author = request.form['author']
        recipe.content = request.form['content']
        recipe.steps = request.form['steps']
        db.session.commit()
        return redirect(url_for('show_recipe', recipe_id=recipe.id))
    return render_template('edit.html', recipe=recipe)

@app.route('/recipe/delete/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    # 查找食譜
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # 刪除食譜
    db.session.delete(recipe)
    db.session.commit()
    
    # 顯示刪除成功消息
    flash('食譜已成功刪除！', 'success')
    
    # 重定向到食譜列表頁面
    return redirect(url_for('index'))

@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        content = request.form['content']
        steps = request.form['steps']
        
        new_recipe = Recipe(
            title=title,
            author=author,
            content=content,
            steps=steps
        )
        try:
            db.session.add(new_recipe)
            db.session.commit()
            return redirect(url_for('index'))
        except IntegrityError:
            db.session.rollback()
            return 'Error: The recipe could not be added.'
    return render_template('add.html')

@app.route('/posts')
def posts():
    return render_template('posts.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
