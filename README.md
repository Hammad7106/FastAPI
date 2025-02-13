FastAPI Project Setup Guide

1- All the dependences which you have to install to run the project are mentioned in pyproject.toml

2- For Database Connection, Go to database.py and add your database url. Similarly go to alembic.ini and paster your Database URL

3- To run the project go to fastapi_project directory by cd fastapi_project then cd fastapi_project

4- In main.py there are all the Endpoints for Users and Candidates

5- In auth.py there is the JWT Token Functionality

6- model.py contains db models

7- serializers.py contains the schemas using pydantic

8- Test Cases are in tests directory 

9- Run Tests by this command python -m pytest --asyncio-mode=auto         


