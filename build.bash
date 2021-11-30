python3 setup.py sdist bdist_wheel
twine upload dist/*
rm -rf build/ dist/ bcf_extras.egg-info/
