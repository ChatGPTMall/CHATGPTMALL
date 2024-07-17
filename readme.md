# CHATGPTMALL INSTALLATION GUIDE


-------

### Environment setup
Install system dependencies : E.g for ubuntu
```shell
$ sudo apt install build-essential python3-dev libpq-dev python3-virtualenv
$ sudo amazon-linux-extras install libreoffice
```

Create virtualenv
```shell
$ virualenv -p python3 venv
```

### Start Project
Activate virtualenv
```shell
$ source venv/bin/activate
```

Install all dependencies
```shell
$ pip install -r requirements.txt
```

Make Migrations
```shell
$ python manage.py makemigrations
```

Run Migration
```shell
$ python manage.py migrate
```

Run Migration
```shell
$ python manage.py collectstatic
```

Start local server ( Testing only )
```shell
$ python manage.py runserver
```

```shell
$ python manage.py test

$ npm i  --legacy-peer-deps  
```


