import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from models import db, Recipe
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from flask import send_from_directory
from datetime import datetime

# 初始化應用
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

# 設置上傳文件夾
UPLOAD_FOLDER = 'uploads/'

# 確保 uploads 資料夾存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 設置上傳路徑
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# 設置上傳文件夾和允許的檔案類型
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# 初始化 db
db.init_app(app)  
migrate = Migrate(app, db)

# 在應用上下文中創建資料表
with app.app_context():
    db.create_all()  # 創建所有資料表

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 前端頁面
@app.route('/')
def index():
    recipes = Recipe.query.all()  # 獲取所有食譜資料
    return render_template('index.html', recipes=recipes)

@app.route('/recipes/<category_name>')
def show_recipes_by_category(category_name):
    # 獲取當前頁碼，預設為第1頁
    page = request.args.get('page', 1, type=int)
    
    # 每頁顯示的食譜數量
    recipes_per_page = 10
    
    # 查詢特定類別的食譜並進行分頁
    pagination = Recipe.query.filter_by(category=category_name).paginate(page=page, per_page=recipes_per_page, error_out=False)
    
    # 傳遞食譜列表和分頁物件到模板
    return render_template('recipes_by_category.html', 
                           category_name=category_name, 
                           recipes=pagination.items,  # 當前頁的食譜
                           pagination=pagination)     # 分頁物件
    
@app.route('/all_recipes')
def all_recipes():
    page = request.args.get('page', 1, type=int)  # 獲取當前頁碼，默認為第1頁
    per_page = 10  # 每頁顯示10個食譜
    recipes = Recipe.query.paginate(page=page, per_page=per_page, error_out=False)  # 查詢食譜並分頁
    return render_template('all_recipes.html', recipes=recipes.items, pagination=recipes)


@app.route('/recipe/<int:recipe_id>')
def show_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe.html', recipe=recipe)

# 編輯食譜
@app.route('/edit/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    
    if request.method == 'POST':
        # 獲取表單資料
        title = request.form['title']
        author = request.form['author']
        content = request.form['content']
        steps = request.form['steps']
        difficulty = request.form['difficulty']
        category=request.form['category'] # 儲存類別
        
        # 預設保持原來的圖片
        image = recipe.image  

        # 檢查是否有新的圖片上傳
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image)  # 保存圖片

        # 更新食譜資料
        recipe.title = title
        recipe.author = author
        recipe.content = content
        recipe.steps = steps
        recipe.difficulty = difficulty
        recipe.image = filename if 'filename' in locals() else recipe.image  # 檢查是否有新的圖片

        db.session.commit()  # 提交更改到資料庫
        return redirect(url_for('index'))  # 重定向回食譜列表頁面
    
    return render_template('edit.html', recipe=recipe)


@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    if recipe:
        db.session.delete(recipe)
        db.session.commit()
        flash("成功刪除食譜", "success")
    else:
        flash("找不到食譜", "error")
    # 返回到上一頁（如果沒有上一頁則返回主頁）
    return redirect(url_for('index'))

@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        content = request.form['content']
        ingredients =request.form['ingredients']
        steps = request.form['steps']
        difficulty = request.form['difficulty']
        created_at = request.form['created_at']  # 新增日期
        category = request.form.get('category')  
        
        # 檢查是否有 'category' 欄位，防止未賦值的情況
        category = request.form.get('category')  # 使用 get() 方法來避免未找到欄位時的錯誤
        if not category:
            flash('Category is required!', 'error')  # 提示用戶選擇分類
            return redirect(url_for('add_recipe'))  # 若沒有 category，則跳轉回新增頁面
        
        # 處理圖片上傳
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename  # 儲存圖片文件名
        
        new_recipe = Recipe(
            title=title,
            author=author,
            content=content,
            ingredients =ingredients,
            steps=steps,
            image=image,  # 儲存圖片文件名
            difficulty=difficulty,  # 儲存難度星級
            category=category,  # 儲存類別
                    )
        try:
            db.session.add(new_recipe)
            db.session.commit()
            return redirect(url_for('index'))
        except IntegrityError:
            db.session.rollback()
            return 'Error: The recipe could not be added.'
    return render_template('add.html')

@app.route('/about')
def about():
    return render_template('about.html')

# 檢查上傳的文件是否符合要求的類型
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    app.run(debug=True)
