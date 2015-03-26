from pyramid.config import Configurator
from ccpweb.resources import Root

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    config.scan()
    app = config.make_wsgi_app()
    config.add_static_view('static', 'ccpweb:static')
    return config.make_wsgi_app()

