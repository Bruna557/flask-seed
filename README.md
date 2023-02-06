# Python Seed

## Run tests
```bash
pytest
```

## Database setup
psql -U postgres
CREATE ROLE users LOGIN PASSWORD '1234' NOINHERIT CREATEDB;
CREATE DATABASE users;
\connect users

CREATE TABLE users(ssn VARCHAR PRIMARY KEY, first_name VARCHAR, last_name VARCHAR, date_of_birth DATE);

GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO users;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO users;

## Run app
export FLASK_APP=users/entrypoints/flask_app.py
export FLASK_DEBUG=1
export PYTHONUNBUFFERED=1
flask run --host=0.0.0.0 --port=5005

## Testing
curl --location --request POST 'http://127.0.0.1:5005/users' \
--header 'Content-Type: application/json' \
--data-raw '{
    "ssn": "111-0001-111",
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1986-08-15"
}'

curl --location --request GET 'http://127.0.0.1:5005/users/111-0001-111'

curl --location --request GET 'http://127.0.0.1:5005/users' \
--header 'Content-Type: application/json' \
--data-raw '{
    "page_size": 4,
    "current_page": 1,
    "first_name": "Ana",
    "date_of_birth": "1986-08-15"
}'

## Patterns and Best Practices
### Repository
The Repository pattern is an abstraction over persistent storage. It hides the boring details of data access by pretending that all of our data is in memory.
It also makes it easy to create a FakeRepository for testing.

### Dependency Inversion
Classic SQLAlchemy would have the model depending on the ORM:

    class OrderLine(Base):
        id = Column(Integer, primary_key=True)

Here we invert the dependency and make the ORM depend on the model; we define the schema separately (orm.py) and define and explicit mapper for
how to convert between the schema and our domain model. The end result will be that, if we call start_mappers, we will be able to easily load and save domain model instances from and to the database.

### Service Layer
By adding a service layer
- Our Flask API endpoints become very thin and easy to write: their only responsibility is doing “web stuff,” such as parsing JSON and producing the right HTTP codes for happy or unhappy cases;
- We have a single place to capture all the use cases for our application.

Cons:
- If your app is purely a web app, your controllers/view functions can be the single place to capture all the use cases;
- Putting too much logic into the service layer can lead to the Anemic Domain anti-pattern; you can get a lot of the benefits that come from having rich domain models by simply pushing logic out of your controllers and down to the model layer, without needing to add an extra layer in between

### Ports and Adapters
Ports and adapters came out of the OO world, and the definition we hold onto is that the port is the interface between our application and whatever it is we wish to abstract away, and the adapter is the implementation behind that interface or abstraction.

Concretely, AbstractRepository is a port, and SqlAlchemyRepository and FakeRepository are the adapters. Entrypoints are adapters too.

### Unit of Work
The Unit of Work (UoW) pattern is an abstraction around data integrity. Each unit of work represents an atomic update. It allows us to fully decouple our service layer from the data layer.
We implemented the UoW class using Python Context Manager; the with keyword is used.
