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


Reminders:
    Replace requirements.txt versions to the last working version for packages or you may encounter pip install errors in godaddy

Errors you may encounter in the futre:
    XAMPP:
        - Apache shutdown unexpectedly
            - https://stackoverflow.com/questions/18300377/how-to-solve-error-apache-shutdown-unexpectedly
        - MySQL shutdown unexpectedly
            - https://stackoverflow.com/questions/18022809/how-to-solve-error-mysql-shutdown-unexpectedly/61859561#61859561
            - https://stackoverflow.com/questions/18022809/how-to-solve-error-mysql-shutdown-unexpectedly/67734073#67734073
        