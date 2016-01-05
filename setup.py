from distutils.core import setup
try:
  from setuptools import setup
  _SETUPTOOLS=True
except:
  try:
    from ez_setup import setuptools
    _SETUPTOOLS=True
  except:
    _SETUPTOOLS=False
import sys,shutil,os,datetime,subprocess,glob
__version__='1.0.0'
def setup_package(install=False,build=False,clean=False):
    kwargs=dict(
      name='pyqsub',
      packages=['pyqsub'],
      version=__version__,
      package_dir={'pyqsub':'.'},
      description='Python module for running jobs on a cluster',
      author='David Pugh',
      author_email='djpugh@gmail.com',
      url='https://github.com/djpugh/pyqsub',
      download_url='https://github.com/djpugh/pyqsub/tarball/v1.0.0',
      entry_points={'console_scripts': ['pyqsub = pyqsub.__init__:__run__']},
      keywords=['cluster','torque','pbs','qsub'],
      classifiers=[])
    if build or 'build_all' in sys.argv or 'build-all' in sys.argv:
        #clean dist dir
        for fname in glob.glob('dist/*'):
            try:
                os.remove(fname)
            except:
                pass
        print ('------\nBUILDING DISTRIBUTIONS\n-----\n')
        clean_package()
        argv=[sys.executable,"setup.py","sdist"]
        subprocess.call(argv)
        clean_package()
        argv=[sys.executable,"setup.py","sdist","--format=gztar"]
        subprocess.call(argv)
        clean_package()
        argv=[sys.executable,"setup.py","bdist_wininst"]
        subprocess.call(argv)      
        clean_package()
        argv=[sys.executable,"setup.py","bdist_wheel"]
        subprocess.call(argv)      
        clean_package()
        argv=[sys.executable,"setup.py","bdist_msi"]
        subprocess.call(argv)
        clean_package()
    elif 'clean_all' in sys.argv or clean or 'clean-all' in sys.argv:
        argv=[sys.executable,"setup.py","clean","--all"]
        subprocess.call(argv)
        try:
            shutil.rmtree('build/')
        except:
            pass
        try:
            shutil.rmtree('pyqsub-'+__version__+'/')
            shutil.mkdir('pyqsub-'+__version__+'/')
        except:
            pass
        if _SETUPTOOLS:
            try:
                shutil.rmtree('pyqsub.egg-info/')
                shutil.mkdir('pyqsub.egg-info/')
            except:
                pass
        try:
            shutil.rmtree('__pycache__/')
        except:
            pass
    elif 'pypi_upload' in sys.argv:
        argv=[sys.executable,"setup.py","sdist","upload", "-r", "pypi"]
        subprocess.call(argv)
        clean_package()
        argv=[sys.executable,"setup.py","sdist","--format=gztar","upload", "-r", "pypi"]
        subprocess.call(argv)
        clean_package()
        argv=[sys.executable,"setup.py","bdist_wininst","upload", "-r", "pypi"]
        subprocess.call(argv)      
        clean_package()
        argv=[sys.executable,"setup.py","bdist_wheel","upload", "-r", "pypi"]
        subprocess.call(argv)      
        clean_package()
        argv=[sys.executable,"setup.py","bdist_msi","upload", "-r", "pypi"]
        subprocess.call(argv)
    else:
        setup(**kwargs)
def clean_package():
    old_argv=sys.argv
    sys.argv=['clean_all']
    setup_package(clean=True)
    sys.argv=old_argv

if __name__=="__main__":
    setup_package()
