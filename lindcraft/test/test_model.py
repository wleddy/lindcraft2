import sys
#print(sys.path)
sys.path.append('') ##get import to look in the working dir.

import os
import pytest
import tempfile

import app
from flask import g, session, request
from users.views.test.test_login import login,logout
from lindcraft.models import Model

@pytest.fixture
def client():
    #db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
    app.app.config['TESTING'] = True
    #print(app.app.config)
    client = app.app.test_client()

    with app.app.app_context():
        print(app.app.config['DATABASE_PATH'])
        app.g.db = app.get_db()
        print(app.g.db)
        
    yield client

    # os.close(db_fd)
 #    os.unlink(app.app.config['DATABASE'])
 #
            
def test_validate_form(client):
    """ensure that validate_form works"""
    with client as c:
        from flask import session, g, request
        result = login(c)
        assert session['user'] == 'admin'
        
        url = "/admin/model/edit/7/"
        data = {
        'id':7,
        'model':'',
        'prod_id':None,
        'price_change_date':'',
        }
        rv = c.post(url, data=data, follow_redirects=True)
        assert b'Date may not be empty' in rv.data
        assert b'Date is not in a known format' not in rv.data
        assert b"Model Name is required." in rv.data
        assert b'You must select an product' in rv.data
    
        data = {
        'id':7,
        'model':'a model',
        'prod_id':1,
        'price_change_date':'12',
        }
        rv = c.post(url, data=data, follow_redirects=True)
        assert b'Date may not be empty' not in rv.data
        assert b'Date is not in a known format' in rv.data
        assert b"Model Name is required." not in rv.data
        assert b'You must select an product' not in rv.data
        assert b'That model name is already taken' not in rv.data
        
def test_make_model(client):
    with client as c:
        from flask import session, g, request
        result = login(c)
        assert session['user'] == 'admin'
    
        url = "/admin/model/edit/0/"
        data = {
        'id':0,
        'model':'A test Model',
        'prod_id':20000,
        'price_change_date':'12/13/2018',
        }
        rv = c.post(url, data=data, follow_redirects=True)
        assert b'Date may not be empty' not in rv.data
        assert b'Date is not in a known format' not in rv.data
        assert b"Model Name is required." not in rv.data
        assert b'You must select an product' not in rv.data
        assert b'That model name is already taken' not in rv.data
        assert b'The price may not be None' in rv.data
        assert b'The price must be a number' not in rv.data
        assert b'That is not a valid product' in rv.data
        
        url = "/admin/model/edit/0/"
        data = {
        'id':0,
        'model':'A test Model',
        'prod_id':2,
        'price_change_date':'12/13/2018',
        'price':'50'
        }
        rv = c.post(url, data=data, follow_redirects=True)
        assert b'Date may not be empty' not in rv.data
        assert b'Date is not in a known format' not in rv.data
        assert b"Model Name is required." not in rv.data
        assert b'You must select an product' not in rv.data
        assert b'That model name is already taken' not in rv.data
        assert b'The price must be a number' not in rv.data
        assert b'The price may not be None' not in rv.data

        #get the list
        url = "/admin/model/"
        rv = c.get(url,follow_redirects=True)
        #import pdb;pdb.set_trace()
        assert b'A test Model' in rv.data
        print(g.db)
        # now delete the test record
        rec = Model(g.db).select_one(where='model = "A test Model"')
        if rec:
            model_id = rec.id
        else:
            model_id = None
            
        url = '/admin/model/delete/{}'.format(model_id)
        rv = c.get(url,follow_redirects=True)
        assert b'Model Deleted' in rv.data
        
        
    
        