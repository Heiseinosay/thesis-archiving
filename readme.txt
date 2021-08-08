prereqs:
    - pipenv
    - python 3.7
    - XAMPP

setup:
    1. cd to where 'pipfile.lock' can be found then install and activate pipenv 
    2. install pipenv packages via "pipenv install"
    3. open XAMPP and start apache and mysql
    4. open mysql admin
    5. import mysql data
    6. setup .env environment variables
        - ask for the vars
        - in the SQLALCHEMY_DATABASE_URI, replace username, pw, and db name with your own mysql configs
    7. execute "run.py" in pipenv

pulling w/ db updates:
    1. pull
    2. import new mysql data