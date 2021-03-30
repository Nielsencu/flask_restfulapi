import datetime
from flask import request, jsonify, make_response, Blueprint
import uuid
from pytz import timezone
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from project.models import Customer,User,db
from functools import wraps
from project import config

backend = Blueprint('frontend', __name__)

singapore = timezone('Asia/Singapore')

@backend.route("/")
def hello_world():
    return jsonify({"hello" : "world"})

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing!'})

        try:
            data = jwt.decode(token,config.SECRET_KEY)
            current_user = User.query.filter_by(public_id = data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# User related views

@backend.route('/api/users', methods=['GET'])
def list_users():
    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['name'] = user.name
        user_data['admin'] = user.admin
        user_data['public_id'] = user.public_id
        output.append(user_data)

    return jsonify({'users' : output})


@backend.route('/api/users/register', methods=['POST'])
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')
    public_id = str(uuid.uuid4())
    data['public_id'] = public_id
    new_user = User(public_id = public_id, name = data['name'], password=hashed_password, admin=True) #For development convenience, admin defaults to true

    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user has been created', "user" : data})

@backend.route('/api/users/<public_id>', methods=['PUT'])
@token_required
def promote_user(public_id):

    user = User.query.filter_by(public_id = public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    user.admin = True
    db.session.commit()

    return jsonify({'message' : 'User is now an admin'})

@backend.route('/api/users/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):

    if not current_user.admin:
        return jsonify({'message' : 'Have no permission!'})

    user = User.query.filter_by(public_id =public_id).first()

    if not user:
        return jsonify({'message' : 'No User found!'})
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message' : 'The User has been deleted', 'public_id' : public_id})

#Customer related views

@backend.route('/api/customers', methods=['GET'])
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

@backend.route('/api/customers/sortedbydob/<n>', methods=['GET'])
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

    output.sort(key = lambda item:item['dob'], reverse=True)

    result = []

    n = int(n)

    if(n > len(output)):
        n = len(output)

    for i in range(n):
        result.append(output[i])
        
    return jsonify({'customer' : result})


@backend.route('/api/customers/<customer_id>', methods=['GET'])
@token_required
def get_customer(current_user,customer_id):

    if not current_user.admin:
        return jsonify({'message' : 'Have no permission!'})

    customer = Customer.query.filter_by(public_id =customer_id).first()

    if not customer:
        return jsonify({'message' : 'No Customer found!'})
    
    customer_data = {}
    customer_data['name'] = customer.name
    customer_data['dob'] = customer.dob
    customer_data['updated_at'] = customer.updated_at
    customer_data['public_id'] = customer.public_id
    return jsonify({'customer' : customer_data})

@backend.route('/api/customers', methods=['POST'])
@token_required
def create_customer(current_user):

    if not current_user.admin:
        return jsonify({'message' : 'Have no permission!'})

    data = request.get_json()
    public_id = str(uuid.uuid4())
    data['public_id'] = public_id
    
    #Current UTC time
    now_utc = datetime.datetime.now(timezone('UTC'))
    #Convert to Singapore time zone
    now_singapore = now_utc.astimezone(singapore)
    #Create new customer
    new_customer = Customer(public_id = public_id, name=data['name'], dob=data['dob'], updated_at = now_singapore)
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'message' : 'New Customer created', 'new_customer' : data})

@backend.route('/api/customers/<customer_id>', methods=['PUT'])
@token_required
def update_customer(current_user, customer_id):

    if not current_user.admin:
        return jsonify({'message' : 'Have no permission!'})

    customer = Customer.query.filter_by(public_id =customer_id).first()

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
    return jsonify({'message' : "Customer's data has been succesfully modified", 'customer' : customer_id})

@backend.route('/api/customers/<customer_id>', methods=['DELETE'])
@token_required
def delete_customer(current_user, customer_id):

    if not current_user.admin:
        return jsonify({'message' : 'Have no permission!'})

    customer = Customer.query.filter_by(public_id =customer_id).first()

    if not customer:
        return jsonify({'message' : 'No Customer found!'})
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message' : 'The customer has been deleted', 'customer_id' : customer_id})

#Login view

@backend.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data['name']
    password = data['password']

    if not username or not password:
        return make_response("Couldn't verify", 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user = User.query.filter_by(name = username).first()
    
    if not user:
        return make_response("Couldn't find the user", 401,{'WWW-Authenticate' : 'Basic realm="Login required!"'})
    
    if check_password_hash(user.password, password):
        token = jwt.encode({'public_id' : user.public_id, 'exp' :datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, config.SECRET_KEY)
        return jsonify({'token' : token.decode('UTF-8')})
    
    return make_response("Couldn't find the user", 401,{'WWW-Authenticate' : 'Basic realm="Login required!"'})
