
from werkzeug.serving import run_simple

from flask_discoverer import Discoverer
from flask_restful import Api, Resource

from adsmutils import ADSFlask

from tugboat.views import IndexView, BumblebeeView, ClassicSearchRedirectView, SimpleClassicView, ComplexClassicView, ComplexClassicArXivView

def create_app(**config):
    """
    Create the application and return it to the user
    :return: flask.Flask application
    """

    if config:
        app = ADSFlask(__name__, local_config=config)
    else:
        app = ADSFlask(__name__)

    app.url_map.strict_slashes = False

    # Add end points
    api = Api(app)
    api.add_resource(IndexView, '/tugboat/index')
    api.add_resource(ClassicSearchRedirectView, '/tugboat/classicSearchRedirect')
    api.add_resource(BumblebeeView, '/tugboat/redirect')
    api.add_resource(SimpleClassicView, '/tugboat/ads')
    api.add_resource(ComplexClassicView, '/tugboat/adsabs')
    api.add_resource(ComplexClassicArXivView, '/tugboat/arxiv')

    Discoverer(app)

    return app

if __name__ == '__main__':
    run_simple('0.0.0.0', 5050, create_app(), use_reloader=False, use_debugger=False)
