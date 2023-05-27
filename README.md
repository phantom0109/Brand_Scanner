# About The Brand Scanner

Transforming how customers discover and engage with curated brands.

## Getting the local server running

- Install `mysql`: https://dev.mysql.com/doc/mysql-installation-excerpt/8.0/en/

```bash
# Clone repository
git clone <repo-link>
cd brandscanner

# creating virtual env
# python3 -m venv path/to/venv
python3 -m venv .venv
source .venv/bin/activate

# create a new database
mysql -u root -p --default-character-set=utf8mb4
CREATE DATABASE brandscanner_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE DATABASE test_brandscanner_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

# Create MySQL users
create user 'py-user' identified by 'p@@sWord';
grant all privileges on brandscanner_db.* to 'py-user';
grant all privileges on test_brandscanner_db.* to 'py-user';
flush privileges;
exit

# install dependencies
pip install --upgrade pip
pip install wheel
pip install -r requirements/requirements-dev.txt

# install pre-commit hooks
pre-commit install

# Provide database authentications
cp .env.sample .env
# update the .env file with mysql username, password and database name
vi .env

# Create database and tables
python manage.py migrate

# Start development server
python manage.py runserver
```


## Deployment

```bash
git push live
```
