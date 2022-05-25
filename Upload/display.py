from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort
from Upload.auth import login_required
from Upload.db import get_db

bp=Blueprint('display',__name__)

@bp.route('/')
@login_required
def index():
    db=get_db()
    # subcat=request.form['subcategory']
    # temp=request.form['template']
    # if cat is None and subcat is None and temp is None:
    categories=db.execute('SELECT category FROM user_permission WHERE user_id=? AND subcategory IS NULL AND template IS NULL',(g.user['id'],)).fetchall()
    return render_template('display/index.html',categories=categories,subcategory=None, template=None)
    # elif subcat is None and temp is None:
    #     subcategory=db.execute('SELECT subcategory FROM user_permission WHERE user_id=? AND category=? AND template IS NULL',(g.user['id'],request.)).fetchall()
    #     return render_template('display/index.html',categories=list(cat),subcategory=subcategory, template=None)
    # else:
    #     template=db.execute('SELECT template FROM user_permission WHERE user_id=? AND category=? AND subcategory=?')
    #     return render_template('display/index.html',categories=cat,subcategory=subcat, template=template)


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
