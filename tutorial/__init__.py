from pyramid.config import Configurator


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.add_route('home', '/')
    config.add_route('plain', '/plain')
    #score
    config.add_route('score', '/score')
    config.scan('.views')
    return config.make_wsgi_app()
