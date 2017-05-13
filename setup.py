from distutils.core import setup
#from setuptools import setup
setup(
  name = 'CellTypeCLassifier',
  packages = ['CellTypeCLassifier'], # this must be the same as the name above
  version = '0.1',
  description = 'Kilosort/phy generated units supervised and unsupervised classification, with the hope to sort them by cell type.',
  author = 'Maxime Beau',
  author_email = 'm.beau047@gmail.com',
  url = 'https://github.com/MS047/CellTypeClassifier', # use the URL to the github repo
  download_url = 'https://github.com/MS047/CellTypeClassifier/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['Kilosort', 'Phy', 'Classifier', 'sklearn', 'Extracellular', 'Spike Sorting'], # arbitrary keywords
  classifiers = [],
)