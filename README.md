# Simple Python API

This API will be used as a mock API in a talk to introduce API testing with Pytest.

## Installation

Requires [Python](https://www.python.org/) 3.7+ to run.

Create virtual environment and activate it

```sh
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies.

```sh
pip install -r requirements.txt
```

And start the server

```sh
uvicorn main:app
```

The API swagger can be acessed in this link: http://127.0.0.1:8000/docs


## License

MIT
