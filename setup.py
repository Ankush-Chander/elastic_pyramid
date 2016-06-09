from setuptools import setup

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyorient',
    'elasticsearch',
    'elasticsearch-dsl',
    'regex',
    'nltk',
    'numpy'
]

setup(name='tutorial',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = tutorial:main
      """,
)
