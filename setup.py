import os
import sys

from setuptools import find_packages, setup
from setuptools.command.install import install
from setuptools.command.build_ext import build_ext as _build_ext
from setuptools.command.sdist import sdist as _sdist
from setuptools.extension import Extension

import polemarch

try:
    from Cython.Distutils import build_ext as _build_ext
    from Cython.Build import cythonize
except ImportError:
    has_cython = False
else:
    has_cython = True


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

RMF = os.path.join(os.path.dirname(__file__), 'polemarch/README.md')
with open(RMF) as readme:
    README = readme.read()

RQF = os.path.join(os.path.dirname(__file__), 'requirements.txt')
with open(RQF) as req:
    REQUIRES = req.read().strip().split('\n')

RQF_git = os.path.join(os.path.dirname(__file__), 'requirements-git.txt')
with open(RQF) as req:
    REQUIRES_git = req.read().strip().split('\n')

if 'compile' in sys.argv:
    use_cython = True
    ext = ".py"
else:
    use_cython = False
    ext = '.c'

extensions_dict = dict((
    ("polemarch.api.v1.filters", ["polemarch/api/v1/filters"+ext]),
    ("polemarch.api.v1.serializers", ["polemarch/api/v1/serializers"+ext]),
    ("polemarch.api.v1.views", ["polemarch/api/v1/views"+ext]),
    ("polemarch.api.base", ["polemarch/api/base"+ext]),
    ("polemarch.api.handlers", ["polemarch/api/handlers"+ext]),
    ("polemarch.api.permissions", ["polemarch/api/permissions"+ext]),
    ("polemarch.api.routers", ["polemarch/api/routers"+ext]),
    ("polemarch.api.urls", ["polemarch/api/urls"+ext]),
    ("polemarch.main.models.base", ["polemarch/main/models/base"+ext]),
    ("polemarch.main.models.hosts", ["polemarch/main/models/hosts"+ext]),
    ("polemarch.main.models.projects", ["polemarch/main/models/projects"+ext]),
    ("polemarch.main.models.tasks", ["polemarch/main/models/tasks"+ext]),
    ("polemarch.main.models.users", ["polemarch/main/models/users"+ext]),
    ("polemarch.main.models.vars", ["polemarch/main/models/vars"+ext]),
    ('polemarch.main.settings', ["polemarch/main/settings"+ext]),
    ('polemarch.main.repo_backends', ["polemarch/main/repo_backends"+ext]),
    ('polemarch.main.context_processors',
     ["polemarch/main/context_processors"+ext]),
))

ext_modules = list(Extension(m, f) for m, f in extensions_dict.items())

if use_cython:
    ext_modules = cythonize(ext_modules)

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # Remove .py and .c files from libs


class Compile(_sdist):
    def __filter_files(self, files):
        for _files in extensions_dict.values():
            for file in _files:
                if file in files:
                    files.remove(file)
        return files

    def make_release_tree(self, base_dir, files):
        if use_cython:
            files = self.__filter_files(files)
        _sdist.make_release_tree(self, base_dir, files)


setup(
    name='polemarch',
    version=polemarch.__version__,
    packages=find_packages(),
    ext_modules=cythonize(ext_modules),
    include_package_data=True,
    license='AGPLv3',
    description='Polemarch is ansible based for orcestration infrastructure.',
    long_description=README,
    author='VST Consulting',
    author_email='sergey.k@vstconsulting.net',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.{8-11}',
        'Operating System :: OS Independent',
        'Programming Language :: Cython',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Utilities',
    ],
    scripts=['polemarchctl'],
    setup_requires=[
        "cython>=0.25.2",
    ],
    install_requires=[
        "django>=1.8,<1.12",
    ] + REQUIRES,
    dependency_links=[
    ] + REQUIRES_git,
    extras_require={
        "apache": [
            "mod_wsgi==4.5.14"
        ]
    },
    cmdclass={
        'install': PostInstallCommand,
        'compile': Compile,
        'build_ext': _build_ext
    },
)
