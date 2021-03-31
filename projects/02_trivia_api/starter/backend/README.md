# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Environment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## SECRET_KEY for DataBase

The flask Server will search for a Environment variable called SECRET_KEY to access the database. Please set this one globally or with an .env file in the flaskr sub-directory.

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

## API Documentation


The following section will explain which endpoints the Trivia API is using to enable other developers to use a customized Frontend.


### Getting Started


Since the Server is currently hosted only locally please use http://127.0.0.1:5000/ as the base URL. For now there are now API Keys needed.


### Used error response codes


If you face any issues with using the API this chapter shall help you to identify the root cause. Errors are returned as JSON ojects in the following format.

```
{
    "success": False,
    "error": 400,
    "message": "bad request, Client Error"
}
```

The API will return four different error types when requests are failing:

- 400: Bad request
- 404: Resource not found
- 405: Method not allowed
- 422: Not processable


### Endpoints


#### GET /categories

- General:
  * Returns a list of all category objects and a success value
- Sample: `curl -X GET http://127.0.0.1:5000/categories`

```
{
    "categories":{
        "1":"Science",
        "2":"Art",
        "3":"Geography",
        "4":"History",
        "5":"Entertainment",
        "6":"Sports"}
    ,"success":true
}

```


#### GET /questions


- General:
  * Returns a list of all paginated questions (10 per page) objects, a success value, the amount of questions in total, and all categories
- Sample: `curl -X GET http://127.0.0.1:5000/questions`

```
{
    "categories": {
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    },
    "questions": [
        {
            "answer": "Apollo 13",
            "category": 5,
            "difficulty": 4,
            "id": 2,
            "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
        },
        {
            "answer": "Tom Cruise",
            "category": 5,
            "difficulty": 4,
            "id": 4,
            "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
        },
        {
            "answer": "Maya Angelou",
            "category": 4,
            "difficulty": 2,
            "id": 5,
            "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
        },
        {
            "answer": "Edward Scissorhands",
            "category": 5,
            "difficulty": 3,
            "id": 6,
            "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
        },
        {
            "answer": "Muhammad Ali",
            "category": 4,
            "difficulty": 1,
            "id": 9,
            "question": "What boxer's original name is Cassius Clay?"
        },
        {
            "answer": "Brazil",
            "category": 6,
            "difficulty": 3,
            "id": 10,
            "question": "Which is the only team to play in every soccer World Cup tournament?"
        },
        {
            "answer": "Uruguay",
            "category": 6,
            "difficulty": 4,
            "id": 11,
            "question": "Which country won the first ever soccer World Cup in 1930?"
        },
        {
            "answer": "George Washington Carver",
            "category": 4,
            "difficulty": 2,
            "id": 12,
            "question": "Who invented Peanut Butter?"
        },
        {
            "answer": "Lake Victoria",
            "category": 3,
            "difficulty": 2,
            "id": 13,
            "question": "What is the largest lake in Africa?"
        },
        {
            "answer": "The Palace of Versailles",
            "category": 3,
            "difficulty": 3,
            "id": 14,
            "question": "In which royal palace would you find the Hall of Mirrors?"
        }
    ],
    "success": true,
    "total_questions": 26
}

```


#### GET /categories/<int:category_id>/questions


- General:
  * Is getting back questions based on a provided category id.
- Sample: `curl -X GET http://127.0.0.1:5000/categories/2/questions`

```
{
    "current_category": 2,
    "questions": [
        {
            "answer": "Escher",
            "category": 2,
            "difficulty": 1,
            "id": 16,
            "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
        },
        {
            "answer": "Mona Lisa",
            "category": 2,
            "difficulty": 3,
            "id": 17,
            "question": "La Giaconda is better known as what?"
        },
        {
            "answer": "One",
            "category": 2,
            "difficulty": 4,
            "id": 18,
            "question": "How many paintings did Van Gogh sell in his lifetime?"
        },
        {
            "answer": "Jackson Pollock",
            "category": 2,
            "difficulty": 2,
            "id": 19,
            "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
        }
    ],
    "success": true,
    "total_questions": 29
}
```


#### POST /questions


- General:
  * Is posting an question object into the database.
- Sample: `curl -X POST http://127.0.0.1:5000/questions -H "Content-Type: application/json" -d '{"question": "test", "answer": "test", "category": 1, "difficulty":1}'`

```
{
    "answer": "curl",
    "category": 1,
    "difficulty": 1,
    "question": "curl",
    "success": true
}
```


#### POST /questions/search>


- General:
  * Is searching case-insensitive in all questions in the questions text. A searchTerm as a string in the request is expected.
- Sample: `curl -X POST http://127.0.0.1:5000/questions/search -H "Content-Type: application/json" -d '{"searchTerm":"Test"}'`

```
{
    "current_category": null,
    "questions": [
        {
            "answer": "test",
            "category": 5,
            "difficulty": 1,
            "id": 45,
            "question": "test"
        }
    ],
    "success": true,
    "total_questions": 29
}
```


#### POST /quizzes


- General:
  * Based on previous asked questions `previous_questions` and `quiz_category` a question will be returend based on the given category and without the previously requested questions to avoid duplicates. If `quiz_category=0` is requestsed a mix of all categories will be used.
- Sample: `curl -X POST http://127.0.0.1:5000/quizzes -H "Content-Type: application/json" -d '{"previous_questions": [], "quiz_category": {"id":0,"type":"click"}}'`

```
{
    "question": {
        "answer": "George Washington Carver",
        "category": 4,
        "difficulty": 2,
        "id": 12,
        "question": "Who invented Peanut Butter?"
    },
    "success": true
}
```


#### DELETE /questions/<int:question_id>


- General:
  * Is deleting an question object in the database based on the id of the question
- Sample: `curl -X DELETE http://127.0.0.1:5000/questions/20`

```
{
    "deleted": 20,
    "success": true
}
```


