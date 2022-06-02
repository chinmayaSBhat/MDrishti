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
    template=template
    if request.method == 'POST':
        file = request.files["file"]                    
        if file:
            df = pd.read_excel(file)
            
    #return render_template('display/index.html')
    columns=tuple(df.columns.values)
    data=tuple(df.itertuples(index=False, name=None))
    print("data", columns)
    return render_template('display/file_content.html',columns=columns,data=data, template=template)

@bp.route('/upload_file_data/<template>', methods=['POST','GET'])
@login_required
def upload_file_data(template):
    db=get_db()
    post_data=[]
    keys=[]
    values=[]
    if request.method=='POST':
        for key in request.form.keys():
            
            keys.append(key)
            values.append(request.form.getlist(key))
            # for value in request.form.getlist(key):
            #     print (key,":",value)
            #     keys.append(key)
            #     values.append(value)
        dict1=zip(keys,values)
        
    #print(dict(dict1))
    df=pd.DataFrame.from_dict(dict(dict1))
    print(df)
    cols = ",".join([str(i) for i in df.columns.tolist()])
    print("cols",cols)
    print(template)
    query="INSERT INTO "+template+"  ("+cols+")" +"VALUES "
    print(query)
    for i,row in df.iterrows():
        print(tuple(row))
        q=query+str(tuple(row))
        print(q)
        #sql = "INSERT INTO `book_details` (`" +cols + "`) VALUES (" + "%s,"*(len(row)-1) + "%s)"
        db.execute(q)
        db.commit()
            
    #return render_template('display/file_content.html')
    return redirect(url_for('display.index'))

@bp.route('/view_Data/<template>', methods=['POST','GET'])
@login_required
def view_Data(template):
    db=get_db()
    templates=(db.execute("SELECT * FROM pragma_table_info(?) ",(template,)).fetchall())
    print(templates)
    templArr=[]
    for temp in templates:
        templArr.append(temp[1])
    q='SELECT * FROM '+template
    d2d=db.execute(q).fetchall()
    return render_template('display/view_data.html',columns=templArr,data=d2d)