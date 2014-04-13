import pprint

import flask
import jinja2

import run_db


web_app = flask.Flask(__name__)

template_loader = jinja2.FileSystemLoader('templates')
web_app.jinja_loader = template_loader


@web_app.route('/')
def index():
    return flask.redirect(flask.url_for('list_runs'))


@web_app.route('/list_runs')
def list_runs():
    return flask.render_template(
        'list_runs.html',
        runs=run_db.get_all_runs())


@web_app.route('/run_details')
def run_details():
    args = flask.request.args
    id = args['id']
    run = run_db.Run(id)
    return flask.render_template(
        'run_details.html',
        run=run,
        debug=pprint.pformat((run.attrs, run.results)))


if __name__ == '__main__':
    web_app.debug = True
    web_app.run()
