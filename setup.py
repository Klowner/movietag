import re
from setuptools import setup

setup(
        name = "movietag",
        version = "0.0.1",
        packages = ['movietag'],
        author = "Mark Riedesel",
        author_email = "mark@klowner.com",
        url = "http://github.com/klowner/movietag/",
        entry_points = {
            "console_scripts": ["movietag = movietag.movietag:main"]
            },
        )
