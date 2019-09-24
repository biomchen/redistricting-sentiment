from setuptools import setup

install_reqs = open('requirements.txt')
lines = install_reqs.readlines()
reqs = [str(each_req) for each_req in lines]

setup(name='redistrict',
      version='0.1',
      description='Simple module to analyze sentiments of LOU redistricting',
      long_description = read_file('README.md'),
      author='Meng Chen',
      author_email='meng.chen03@gmail.com',
      url='https://github.com/biomchen/2019_LOU_Redistricting_Sentiment',
      license='MIT',
      install_requires=reqs,
      keywords = 'sentiment Frederick Maryland redistricting')
