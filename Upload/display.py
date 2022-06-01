from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify,send_file
)
from werkzeug.exceptions import abort
from Upload.auth import login_required
from Upload.db import get_db
import pandas as pd 

bp=Blueprint('display',__name__)

@bp.route('/')
@login_required
def index():
    db=get_db()
    categories=db.execute('SELECT category FROM user_permission WHERE user_id=? AND subcategory IS NULL AND template IS NULL',(g.user['id'],)).fetchall()
    return render_template('display/index.html',categories=categories,subcategory=None, template=None)

@bp.route('/get_subcat/<category>', methods=['POST','GET'])
@login_required
def get_subcat(category):
    db=get_db()
    subcategory=(db.execute('SELECT subcategory FROM user_permission WHERE user_id=? AND category=? AND template IS NULL AND subcategory IS NOT NULL',(g.user['id'],category)).fetchall())
    subcatArr=[]
    for sc in subcategory:
        scObj={}
        scObj['subcategory']=sc['subcategory']
        subcatArr.append(scObj)
    return jsonify({'subcategory':subcatArr})

@bp.route('/get_template/<sc>', methods=['POST','GET'])
@login_required
def get_template(sc):
    db=get_db()
    templates=(db.execute('SELECT template FROM user_permission WHERE user_id=? AND subcategory=?  AND template IS NOT NULL',(g.user['id'],sc)).fetchall())
    templArr=[]
    for temp in templates:
        tempObj={}
        tempObj['template']=temp['template']
        templArr.append(tempObj)
    return jsonify({'template':templArr})

@bp.route('/download_file/<template>', methods=['POST','GET'])
@login_required
def download_file(template):
    db=get_db()
    templates=(db.execute("SELECT * FROM pragma_table_info(?) ",(template,)).fetchall())
    print(templates)
    templArr=[]
    for temp in templates:
        templArr.append(temp[1])

    data = pd.DataFrame([],columns=templArr)
    data.to_excel('Upload/table_template/sample_data.xlsx', sheet_name='sheet1', index=False)

    return send_file('table_template/sample_data.xlsx', as_attachment=True)

@bp.route('/upload_file/<template>', methods=['POST','GET'])
@login_required
def upload_file(template):
    if request.method == 'POST':
        file = request.files["file"]                    
        if file:
            df = pd.read_excel(file)
            
    #return render_template('display/index.html')
    titles=pd.DataFrame([],columns=df.columns.values)
    return render_template('display/file_content.html',tables=[df.to_html(index=None)],titles=[titles.to_html(classes='data',index=None)])

