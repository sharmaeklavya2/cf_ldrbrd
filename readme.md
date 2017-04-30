# Codeforces leaderboard

A webapp that stores some usernames and shows a codeforces
contest leaderboard only for those usernames.

This webapp has only been tested on Ubuntu 16.04.
It is compatible with python 3.5+.

To use this webapp, you have to add a list of users who will be shown on the leaderboard.
To do that, you can either use the form on the index page of the webapp,
or you can add objects of the type `django.contrib.auth.models.User` to the database
whose `username` field is the same as their username on Codeforces.
That can be easily done using Django's admin interface (`/admin/`).

After users have been registered, you can see their relative performance at `/ldrbrd/<contest_id>/`.
This page will show the relative performance of all users (even the superuser)
registered on this webapp who took part in that codeforces contest.

## Deploying on Heroku

### Required environment variables

* `SECRET_KEY`: This will be used as `django.conf.settings.SECRET_KEY`.
* `HEROKU`: Set this variable to any value.
  The presence of this environment variable makes django use settings appropriate for Heroku.

### Setup instructions

1.  Create a heroku app.
2.  Setup environment variables as specified above.
3.  Push code to heroku app.
4.  Run a one-off dyno (using `heroku run bash`) and run these commands on it:
    * `python manage.py migrate`.
    * `python manage.py collectstatic`.
    * `python manage.py createsuperuser`. Now fill out details of the superuser.

## Deploying locally for testing

For setting up a development environment, you must install the required dependencies.
It is recommended to use a virtualenv.

### Quick start

    pip install -r requirements/dev.txt.
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Now go to http://localhost:8000 to check out your webapp.

You can find the admin interface at http://localhost:8000/admin/.

## Settings

Settings can be found in `project_conf/settings/`:

* `heroku.py` contains settings to run the webapp on Heroku.
* `default.py` contains settings to run the development environment.
* `__init__.py` contains the common settings.

If you want to modify settings, it is recommended to copy `default.py`
to a new file `local.py` and make changes there, to avoid messing things up.
`local.py` overrides `default.py`. `local.py` is included in `.gitignore`.

We use SQLite by default for development and testing.
You can change settings to use something else.

We use whitenoise to serve static assets.

To improve the look of web pages, download `bootstrap.css` and `bootstrap.js`
and place them in a directory named `extstatic`.

## Directory structure

* `devel` - Tools to help with development and testing.
* `main` - The main django app.
* `project_conf` - Project settings. Also contains root urlconf and wsgi.py.
* `requirements` - Project requirements for dev and heroku.
* `templates` - all templates used with Django's templating system.
* `static` - all static files created for this project.

## Automated testing

* pyflakes - linter and static checker.
  Use it from `devel/lint_all.py`.
  `devel/lint-all.py` also uses a custom linter.
* `python manage.py test` - django backend tests.

We also have a .travis.yml to run tests automatically on Travis CI.
The travis helper scripts are located in `devel/travis/`.

## License

All code is licensed under [GNU GPLv3](http://www.gnu.org/licenses/gpl-3.0.txt).
