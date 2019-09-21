from setuptools import setup
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt')
reqs = [str(each_req.req) for each_req in install_reqs]

setup(name='redistrict',
      version='0.1',
      description='Simple API to analyze sentiments of LOU redistricting',
      url='https://github.com/biomchen/2019_LOU_Redistricting_Sentiment',
      author='Meng Chen',
      author_email='meng.chen03@gmail.com',
      license='MIT',
      install_requires=reqs)
