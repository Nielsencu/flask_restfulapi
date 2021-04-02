# Flask Restful API

Flask Restful API, uses docker for easy deployment and JWT for authentication.

## Set up

Once you have cloned the repo, install dependencies by:

```cli
cd services/web/
pipenv install
```

This command will read the Piplock file and install all the required dependencies.

Activate virtual environment :

```cli
pipenv shell
```

Configure postgres database password, database username, and database name by going to `config.py` in `/services/web/project/` and also change it in the environment variables in `docker-compose.yml` which is in root.

## Launch the Server

To launch the server use this command:

```cli
docker-compose up -d --build
```

To check for errors:

```cli
docker-compose logs -f
```

## Routes

**GET** `http://0.0.0.0:5000/`

This base route can be used to check if the API is currently running. If the server is running there will be a response :

```json
{
    "hello": "world"
}
```


### Register a user

**POST** `http://0.0.0.0:5000/api/users/register`

Body of **request** must be JSON. Sample:

```json
{
    "message": "New user has been created",
    "user": {
        "name": "Admin",
        "password": "12345",
        "public_id": "cc170fb4-352a-4705-b8cf-cf07ef1de1af"
    }
}
```

### Get list of all users

No body required. Will return list of all users

**GET** `http://0.0.0.0:5000/api/users`

Sample **Response**:

```json
{
    "users": [
        {
            "admin": true,
            "name": "Admin",
            "public_id": "cc170fb4-352a-4705-b8cf-cf07ef1de1af"
        }
    ]
}
```

### Delete an user

No body required. x-access-token required in the headers. User's public id will come from the URL.

**DELETE** `http://0.0.0.0:5000/api/users/:public_id`

**Response** for the delete will just be the public_id for the deleted user

```json
{
    "message": "The User has been deleted",
    "public_id": "cc170fb4-352a-4705-b8cf-cf07ef1de1af"
}
```

If no customer is matched with the public_id :
```json
{
    "message": "No User found!"
}
```


### Login and get a token

**POST** `http://0.0.0.0:5000/login`

Body of **request** must be JSON. Sample:

```json
{
  "name": "Admin",
  "password": "12345"
}
```

Valid request will return a JSON string **response** like this sample:

```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwdWJsaWNfaWQiOiJjYzE3MGZiNC0zNTJhLTQ3MDUtYjhjZi1jZjA3ZWYxZGUxYWYiLCJleHAiOjE2MTczMzYxNjd9.t_ipIOpplnIN9tC0Qh877d5R6ZOLNnzwai8KTw4rpuU"
}
```

### Get list of all customers

No body required. x-access-token required in the headers. Will return list of all customers.

**GET** `http://0.0.0.0:5000/api/customers`

Sample **Response**:

```json
{
    "customers": [
        {
            "dob": "1998-02-05",
            "name": "Swen",
            "updated_at": "2021-04-02 03:34:43.325076+00"
        },
        {
            "dob": "2005-02-15",
            "name": "Palm",
            "updated_at": "2021-04-02 03:34:44.892941+00"
        },
        {
            "dob": "1998-05-25",
            "name": "Pam",
            "updated_at": "2021-04-02 03:34:46.310163+00"
        }
    ]
}
```

### Get n youngest customers

No body required. x-access-token required in the headers. Will return n youngest customers (from top to bottom).

**GET** `http://0.0.0.0:5000/api/customers/sortedbydob/:n`

Sample **Response**:

```json
{
    "customer": [
        {
            "dob": "2005-02-15",
            "name": "Palm",
            "updated_at": "2021-04-02 03:34:44.892941+00"
        },
        {
            "dob": "1998-05-25",
            "name": "Pam",
            "updated_at": "2021-04-02 03:34:46.310163+00"
        },
        {
            "dob": "1998-02-05",
            "name": "Swen",
            "updated_at": "2021-04-02 03:49:50.540073+00"
        }
    ]
}
```

### Get a specific customer

No body required. x-access-token is required in the headers. Will get details of specific customer based on the matching public_id of the customer.

**GET** `http://0.0.0.0:5000/api/customers/:public_id`

Sample **response**:

```json
{
    "customer": {
        "dob": "1998-02-05",
        "name": "Swen",
        "public_id": "a7ec53cd-e8e1-416e-9a0f-8a25b0f6f40b",
        "updated_at": "2021-04-02 03:34:43.325076+00"
    }
}
```

### Add a new customer

Body must be JSON. x-access-token required in the headers. Adds a new customer. Sample:

**POST** `http://0.0.0.0:5000/api/customers`

```json
{
  "name": "Swen",
  "dob": "1998-02-05"
}
```

### Update customer

Body must be JSON. x-access-token required in the headers. Updates an existing customer based on the matching public_id. Customer's public id will come from the URL. Sample:

**PUT** `http://0.0.0.0:5000/api/customers/:public_id`

```json
{
  "name": "Swen",
  "dob": "2010-05-25"
}
```

If no customer is matched with the public_id :
```json
{
    "message": "No Customer found!"
}
```

### Delete a customer

No body required. x-access-token required in the headers. Customer's public id will come from the URL.

**DELETE** `http://0.0.0.0:5000/api/customers/:public_id`

**Response** for the delete will just be the public_id for the deleted customer

```json
{
    "customer_id": "5139fcc0-e59f-4410-866d-caf8393a79ce",
    "message": "The customer has been deleted"
}
```

If no customer is matched with the public_id :
```json
{
    "message": "No Customer found!"
}
```

## Tokens

API uses JSON web tokens to authenticate users. The token must be included as a `x-access-token` header in the request with the value set to the token string.

Example header:

```js
"token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwdWJsaWNfaWQiOiJjYzE3MGZiNC0zNTJhLTQ3MDUtYjhjZi1jZjA3ZWYxZGUxYWYiLCJleHAiOjE2MTczMzYxNjd9.t_ipIOpplnIN9tC0Qh877d5R6ZOLNnzwai8KTw4rpuU"
```