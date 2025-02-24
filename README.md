# HTTP protocol client/server test suite

This is a crude HTTP client/server accompanied by a test suite consisting of unit, integration and acceptance tests.

The main goal of all this is to try to explain how to test an HTTP protocol as defined by the RFC9110.

## Usage

Start the server
```bash
$ python server.py -p "hello right back"
```

Use the client to make a request
```bash
$ python client.py -r "request body"
```

You should see the request and the response in the logs
```bash
[2025-02-23 16:43:49.459709]
Client_request:
HTTP/1.1 200 OK
User-Agent: CrappyClient/0.0.1
Content-Type: text/plain

request body

Client_response:
HTTP/1.1 200 OK
Server: CrappyServer/0.0.1
Content-Type: text/plain

hello right back
```

Display help

```bash
$ python client.py -h

$ python server.py -h
```

## Installation

Clone this repository.

Bootstrap the virtual environment
```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
```

Update `pip` and install `uv`
```bash
$ pip install --upgrade pip
$ pip install uv
```

Install the rest of the dependencies
```bash
$ uv sync
```

## Tests and linting

Run tests
```bash
$ pytest -v
```

Run linting
```bash
$ ruff check
$ mypy .
```

## Test strategy

todo summary

mention theory of testing protocols (rules, semantics)

### Unit tests

these are unit tests for the client and for the server, where the other side is merely mocked

these tests verify the logic of either component in isolation, no actual network calls should happen here

we are interested in the individual pieces of code are behaving in a way that we can verify to be compliant with the protocol we are interested to test

however, the main goal of this layer is to provide quick feedback on changes to developers rather than full compliance verification

### Integration tests

these are tests that exercise both components together at the same time, little to no mocking should happen here

the difference to acceptance testing is that we take a lot of shortcuts to the configuration and especially the test environment for this setup

we do not mind that the system is not running in full production configuration/environment, the point here is to verify the two components can talk to each other and that their communication is compliant with the protocol

arguably this is the best cost to value layer of the test suite

### Acceptance tests

this is the most valuable, but also the most expensive layer of the test suite

here the client and server should be deployed in an environment and configuration that resembles the production as close as possible

(include diagram)

mention two generals' problem

### Assumptions

### Test environment

### Risk

### Verification criteria
