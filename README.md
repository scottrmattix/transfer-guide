# Team B-27 Transfer Guide Project

A website to assist students transferring into UVA transfer their credits

## Live website
The live site of the project can be found at <https://transfer-guide.herokuapp.com/>

## Development Environment
It is recommended to use a virtual environment when working on Python projects to keep dependencies local. Create one with
```
python -m venv env
```
Then source the activation script
```
source ./env/bin/activate
```
Then run
```
python -m pip install -r requirements.txt
```
to install dependencies
```
deactivate
```
to end the virtual environment session

If you need to add new dependencies run
```
pip freeze > requirements.txt
```
After you have installed the new dependency, please make sure you are in your virtual environment before doing this.
