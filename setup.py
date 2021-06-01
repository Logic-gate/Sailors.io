from setuptools import setup

setup(name='Jolla Update App',
      version='1.0',
      description='OpenShift App',
      author='mad_dev@linuxmail.org',
      author_email='example@example.com',
      url='http://www.sysbase.org',
     install_requires=['Flask>=0.10.1', 'urllib3==1.26.5', 'feedparser==5.2.1','beautifulsoup4==4.4.1', 'ascii-graph==1.1.3', 'selenium==2.52.0', 'tabulate==0.7.5', 'pythonwhois==2.4.3', 'WTForms==2.1', 'Flask-WTF==0.12', 'pymongo==3.2.1', 'flask-paginate','itsdangerous==0.24', 'click==6.3', 'Flask-Login==0.3.4', "Flask-Mail==0.9.1", "Markdown==2.6.5", "MarkupSafe==0.18", "Flask-Misaka", "Flask-PageDown==0.2.1"])