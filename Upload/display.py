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
    templArr=[]
    flg=0
    for temp in templates:
        if flg!=0:
            templArr.append(temp[1])
        flg=1
    flg=0
    data = pd.DataFrame([],columns=templArr[1:])
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
        dict1=zip(keys,values)
        
    #print(dict(dict1))
    df=pd.DataFrame.from_dict(dict(dict1))
    cols = ",".join([str(i) for i in df.columns.tolist()])
    query="INSERT INTO "+template+"  ("+cols+")" +"VALUES "
    print(query)
    for i,row in df.iterrows():
        print(tuple(row))
        q=query+str(tuple(row))
        print(q)
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
    return render_template('display/view_data.html',columns=templArr,data=d2d,template=template)


def get_data(id, template):
    q="SELECT * FROM "+template+" WHERE id="+str(id)
    d=get_db().execute(q).fetchone()

    if d is None:
        abort(404, f"Content id {id} doesn't exist.")
    return d


@bp.route('/<template>/<int:id>/update', methods=('GET','POST'))
@login_required
def update(id,template):
    db=get_db()
    templates=(db.execute("SELECT * FROM pragma_table_info(?) ",(template,)).fetchall())
    columns=[]
    for temp in templates:
        columns.append(temp[1])

    d=get_data(id,template)
    
    post_data=[]
    keys=[]
    values=[]
    if request.method=='POST':
        for key in request.form.keys():           
            keys.append(key)
            values.append(request.form.getlist(key))
        dict1=zip(keys,values)
        df=pd.DataFrame.from_dict(dict(dict1))
        cols = df.columns.tolist()
        vals=df.iloc[0].tolist()
        query="UPDATE "+ template+ " SET "
        for i in range(len(cols)):
            query+= cols[i]+"= '"+vals[i]+"', "
        query=query[:-2]+" WHERE id="+str(id)
        print(query)
        db.execute(query)
        db.commit()
        return redirect(url_for('display.view_Data',template=template))
    
    return render_template('display/update.html',d=d,columns=columns,template=template )

@bp.route('/<template>/<int:id>/delete', methods=('POST',))
@login_required
def delete(id,template):

    db=get_db()
    q="DELETE FROM "+template +" WHERE ID="+str(id)
    print(q)
    db.execute(q)
    db.commit()
    return redirect(url_for('display.view_Data',template=template))