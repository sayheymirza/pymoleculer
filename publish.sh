# rm dist
rm -rf dist
# build
python3 setup.py sdist bdist_wheel
# publish
python3 -m twine upload -r testpypi dist/*