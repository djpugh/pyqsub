from distutils.core import setup

__version__='1.0.0'
setup(
  name = 'pyqsub',
  packages = ['pyqsub'],
  version = __version__,
  description = 'Python module for running jobs on a cluster',
  author = 'David Pugh',
  author_email = 'djpugh@gmail.com',
  url = 'https://github.com/djpugh/pyqsub',
  download_url = 'https://github.com/djpugh/pyqsub/tarball/1.0.0',
  keywords = ['cluster','torque','pbs','qsub'],
  classifiers = [],
)