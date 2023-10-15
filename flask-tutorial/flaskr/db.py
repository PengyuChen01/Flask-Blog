import sqlite3

import click

#import curren_app: current active application instance, g:store and share data during the life of a request
from flask import current_app, g

#connecting to the SQLite database and return data base connection
def get_db():
    #if db is not not connect in g, establish the connection
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'],
        detect_types = sqlite3.PARSE_DECLTYPES
        )
    #row_factory allow access the rows and return a query name 
    g.db.row_factory = sqlite3.Row
    return g.db

#close the database connection
def close_db(e=None):
    #retrieve the database connection from db, is no connection is find return none
    db = g.pop ('db',None)

    if db is not None:
        db.close()

#initialize the database
def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f: #opens schema.sql file relative to the flaskr package 
        db.executescript(f.read().decode('utf8')) #read binary, decode and execute the sql content in db.
#when user enter init-db the init_db_command will be called that clear the exist data and create new table and output initialized the database.
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db) # tear down process in app: call close_db method to close the connection
    app.cli.add_command(init_db_command) # add init_db_command that when type init-db it will clear exisiting data and create new tables





