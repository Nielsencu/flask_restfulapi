import datetime
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from pytz import timezone
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
from init import create_app
from models import Customer,User,db

singapore = timezone('Asia/Singapore')

app = create_app()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing!'})

        try:
            data = jwt.decode(token,app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id = data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated
@app.route('/createuser', methods=['POST'])
@token_required
def create_user(current_user):
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(public_id = str(uuid.uuid4()), name = data['name'], password=hashed_password, admin=False)

    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user has been created'})

@app.route('/user/<public_id>', methods=['PUT'])
def promote_user(current_user, public_id):

    user = User.query.filter_by(public_id = public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    user.admin = True
    db.session.commit()

    return jsonify({'message' : 'User is now an admin'})

@app.route('/customer', methods=['GET'])
@token_required
def get_all_customers(current_user):

    if not current_user.admin:
        return jsonify({'message' : 'Have no permission!'})

    customers = Customer.query.all()

    output = []

    for customer in customers:
        customer_data = {}
        customer_data['name'] = customer.name
        customer_data['dob'] = customer.dob
        customer_data['updated_at'] = customer.updated_at
        output.append(customer_data)

    return jsonify({'customers' : output})

@app.route('/customer/sortedbydob/<n>', methods=['GET'])
@token_required
def get_n_youngest_customers(current_user,n):

    if not current_user.admin:
        return jsonify({'message' : 'Have no permission!'})

    customers = Customer.query.all()

    output = []

    for customer in customers:
        customer_data = {}
        customer_data['name'] = customer.name
        customer_data['dob'] = customer.dob
        customer_data['updated_at'] = customer.updated_at
        output.append(customer_data)

    output.sort(key = lambda item:item['dob'])

    result = []

    n = int(n)

    if(n > len(output)):
        n = len(output)

    for i in range(n):
        result.append(output[i])
        
    return jsonify({'customer' : result})


@app.route('/customer/<customer_id>', methods=['GET'])
@token_required
def get_customer(current_user,customer_id):

    if not current_user.admin:
        return jsonify({'message' : 'Have no permission!'})

    customer = Customer.query.filter_by(id =customer_id).first()

    if not customer:
        return jsonify({'message' : 'No Customer found!'})
    
    customer_data = {}
    customer_data['name'] = customer.name
    customer_data['dob'] = customer.dob
    customer_data['updated_at'] = customer.updated_at
    return jsonify({'customer' : customer_data})

@app.route('/customer', methods=['POST'])
@token_required
def create_customer(current_user):

    if not current_user.admin:
        return jsonify({'message' : 'Have no permission!'})

    data = request.get_json()
    
    #Current UTC time
    now_utc = datetime.datetime.now(timezone('UTC'))
    #Convert to Singapore time zone
    now_singapore = now_utc.astimezone(singapore)
    #Create new customer
    new_customer = Customer(name=data['name'], dob=data['dob'], updated_at = now_singapore)
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'message' : 'New Customer created'})

@app.route('/customer/<customer_id>', methods=['PUT'])
@token_required
def update_customer(current_user, customer_id):

    if not current_user.admin:
        return jsonify({'message' : 'Have no permission!'})

    customer = Customer.query.filter_by(id =customer_id).first()

    if not customer:
        return jsonify({'message' : 'No Customer found!'})

    data = request.get_json()

    if 'name' in data.keys():
        customer.name = data['name']
    if 'dob' in data.keys():
        customer.dob = data['dob']
    #Current UTC time
    now_utc = datetime.datetime.now(timezone('UTC'))
    #Convert to Singapore time zone
    now_singapore = now_utc.astimezone(singapore)
    #Change updated at
    customer.updated_at = now_singapore

    db.session.commit()
    return jsonify({'message' : "Customer's data has been succesfully modified"})

@app.route('/customer/<customer_id>', methods=['DELETE'])
@token_required
def delete_customer(current_user, customer_id):

    if not current_user.admin:
        return jsonify({'message' : 'Have no permission!'})

    customer = Customer.query.filter_by(id =customer_id).first()

    if not customer:
        return jsonify({'message' : 'No Customer found!'})
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message' : 'The customer has been deleted'})

@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response("Couldn't verify", 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user = User.query.filter_by(name = auth.username).first()

    if not user:
        return make_response("Couldn't find the user", 401,{'WWW-Authenticate' : 'Basic realm="Login required!"'})
    
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.public_id, 'exp' :datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})
    
    return make_response("Couldn't find the user", 401,{'WWW-Authenticate' : 'Basic realm="Login required!"'})

if __name__ == '__main__':
    app.run(debug=True)
