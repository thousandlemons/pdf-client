# PDF Client

This is a python client library to provide a more pleasant experience with [pdf-server](https://github.com/nathanielove/pdf-server)

## Table of Content

* [Install](#release)
* [Quickstart](#quickstart)
	* [Config & API Wrappers](#config-wrapper)
	* [Multithreaded Text Processing](#multith)
* [Module `pdf_client.config`](#config)
	* [`load_from_file()`](#loadff)
	* [Update Configuration at Runtime](#update-config)
* [Class `MultiThreadWorker`]('#worker')
	* [Workflow](#workflow)
	* [Parameters in Constructor](#params)
	* [`start()`](#start)
	* [Logging](#Logging)
* [Package `pdf_client.api`](#api)
* [Appendix](#Appendix)
	* [More Examples on `pdf_client.api` Modules](#api-example)
	* [More Examples on `MultiThreadWorker ` Constructor](#worker-example)
	* [A Recipe of Multithreaded Text Processing: Removing Digits](#Recipe)


## <a name="release" style="color: #000;"></a> Install

The latest release is pdf-client-2.0, released on 9 Sep 2016.

To install the package using pip:

```bash
$ pip install pdf-client
```

## <a name="quickstart" style="color: #000;"></a> Quickstart

### <a name="config-wrapper" style="color: #000;"></a> Config & API Wrappers

First, create a configuration file `config.json` in your project directory:

```json
{
  "base_url": "http://<YOUR_DOMAIN>/api/v1/",
  "auth_class": "HTTPBasicAuth",
  "auth_args": ["<MY_USERNAME>", "<MY_PASSWORD>"]
}
```
Then, create a `main.py` and try the following:

```python
from pdf_client import config
from pdf_client.api import book

config.load_from_file('config.json')	# load configuration
book_list = book.List().execute()		# send HTTP request to RESTful API
print(book_list)
```

The result will be a `list` of `dict`s, for example

```python
[{'title': 'Sample Book', 'root_section': 779, 'id': 2}]
```

### <a name="multith" style="color: #000;"></a> Multithreaded Text Processing

First, make sure you have a configuration file as said in the previous section.

Then, create a class that extends `TextProcessor`:

```python
from pdf_client.multithread.processor import TextProcessor

class ExampleProcessor(TextProcessor):
	def process(self, text, section_id):
		# do some stuff here
		# ...
		return text
```

Finally, create a worker and start:

```python
from pdf_client import config
from pdf_client.multithread.worker import MultiThreadWorker
from demo import ExampleProcessor		# the one we just created

config.load_from_file('config.json')	# load configuration

processor = ExampleProcessor()			# the text processor we just created
worker = MultiThreadWorker(processor=processor
                           book=3,				# book id
                           threads=10,			# total no. of threads
                           create=True,			# create a new version
                           name='New Version')	# new version name

completed = worker.start()	# start the worker and return an iterator
for future in completed:	# the iterator will loop in the order of completion
	section_id, text = future.result()
	print('Completed section ID: {id}'.format(id=section_id))

```

## <a name="config" style="color: #000;"></a> Module `pdf_client.config`

### <a name="loadff" style="color: #000;"></a> `load_from_file()`

This method loads a json file as global configuration.

There are three fields in the json file:

* `base_url`: the base url of the pdf server. (e.g. "http://127.0.0.1:8000/api/v1/" if you are running the django server on localhost)
* `auth_class` *(optional)*: one of the classes in `request.auth` package - `HTTPBasicAuth`, `HTTPDigestAuth` or `HTTPProxyAuth`
* `auth_args` *(optional)*: arguments to be passed into the constructor of `auth_class`

### <a name="update-config" style="color: #000;"></a> Update Configuration at Runtime

There are methods to be called at runtime to load/update the global configuration:

* `set_base_url(base_url)`
* `set_auth(auth)` - see "[Authentication](http://docs.python-requests.org/en/master/user/authentication/)" from package `requests`
* `set_basic_auth(username, password)`, as a shortcut


## <a name="worker" style="color: #000;"></a> Class `MultiThreadWorker`

### <a name="workflow" style="color: #000;"></a> Workflow

Text processing jobs are pretty similar. They always do the following:

1. Specify a root node to start with, then recursively,
* Get the immediate text from a section with a specific "source" version ID
* Process/digest the text
* Optionally, post the processed text back to the server, with a specific "target" version ID.

Hence, the `MultiThreadWorker` in `pdf_client.multithread.worker` module implements the typical workflow, and handles all the details for you.


### <a name="params" style="color: #000;"></a> Parameters in Constructor

| Parameter | Type | Explanation | 
| --- | --- | --- |
| `processor` | `TextProcessor` | An object of any subclass of `TextProcessor`
| `threads` | `int` | Total number of threads used in parallel. <br> The default value is 10.
| `book` | `int` | The book id to start as the root section. <br> If this parameter is left blank, the `section` parameter must be present.
| `section` | `int` | The section id to start as the root section. <br> If `book` is present, this parameter will be ignored.
| `source` | `int` | The source version id, used by the worker to get the text content from the server. <br> If blank, the first version id ("Raw" by default) returned in the `/version/list/` API will be used. 
| `target` |`int` | The target version id, used by the worker to post the processed texts back to the server. <br> If left blank, the worker will check the `create` parameter. <br> If both this parameter and `create` are blank, the worker is in read-only mode, and no text will be posted to the server.
| `create` | `bool` | Set it `True` to create a version on the server as `target_version`. <br> If `target_version` is present, this parameter will be ignored, and no version will be created on the server. 
| `name` | `string` | The name of the version to be created. <br> This parameter must be present together with `create`.


### <a name="start" style="color: #000;"></a> `start()`

Call this method to start the worker immediately.

It will return an iterator over [`concurrent.futures.Future`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Future) objects, in the order of completion. Under the hood, it returns the result of [`concurrent.futures.as_completed()`](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Future). Let's consider this example:

```python
...
completed = worker.start()
for future in completed:
	section_id, text = future.result()
	print("Completed {id}".format(id=section_id))
```

Although the text processing jobs are submitted to the worker threads by pre-order tree traversal, they may complete in a different order, since network IO may take different amount of time. So the `for` loop here gives whichever `Future` completes first, and blocks when waiting for the threads, until there is one completed.

However, **if you pass incorrect values or combinations of parameters to the constructor, an empty `list` will be returned**. To check this, you can either enable logging (see the section below), or do this:

```python
completed = worker.start()
if not completed:
	# do something to handle error
else:
	# do things as expected
```

### <a name="Logging" style="color: #000;"></a> Logging

Since the text processing may take a really long time, you can use logging to monitor the progress or record anything that went wrong.

**DON'T use `print()` to show the progress while looping through the `Future`s**. Instead, enable INFO-level logging of this module:

```python
import logging
import pdf_client

logging.basicConfig()
logging.getLogger(pdf_client.multithread.worker.__name__).setLevel(logging.INFO)
```

The logs generated in this module are pretty comprehensive. They contain the progress and any exception that occured.

## <a name="api" style="color: #000;"></a> Package `pdf_client.api`

This package provide wrapper modules for the APIs in the [pdf-server](https://github.com/nathanielove/pdf-server/tree/improve/doc) project.

Basically, for whatever parameter in the URLs, just pass them to the constructor in order. For example,

```python
from pdf_client.api import version, book, content

version.Detail(3)			# ==> /version/detail/3/
book.Toc(2)					# ==> /book/toc/2/
content.Immediate(3260, 3)	# ==> /content/immediate/3206/3/
```

For json data in request message body, use keyword arguements in the constructor. For example,

```python
version.Update(5, name="Another Name").execute()
```

Please refer to [Appendix](#api-example) to see more example on the argument keywords.

Then, by calling `execute()` on the object you created, the library will send the HTTP request to the RESTful server. It will return the python `list` or `dict` object (or just `string` for `content` module) if the RESTful API returns anything. 

If the operation is successful and the API does not return anything (e.g. delete a version), it will return `True`. If anything goes wrong (any exception, error, or the API returns a different status code than expected) within the `execute()`, it will return `False`

## <a name="Appendix" style="color: #000;"></a> Appendix

### <a name="api-example" style="color: #000;"></a> More Examples on `pdf_client.api` Modules

Create a version:

```python
from pdf_client import config
from pdf_client.api import version

config.load_from_file('config.json')
version.Create(name="My New Version").execute()
```

Post text to the server:

```python
from pdf_client import config
from pdf_client.api import content

config.load_from_file('config.json')
content.Post(3235, 20, text="my new text").execute()
```

Write a whole book to file:

```python
from pdf_client import config
from pdf_client.api import book, content

config.load_from_file('config.json')
root_section = book.List().execute()[0]['root_section']
text = content.Aggregate(root_section).execute()

with open('book.txt', 'w+') as file:
	file.write(text)

```

### <a name="worker-example" style="color: #000;"></a> More Examples on `MultiThreadWorker ` Constructor

Get the entire book in the default version:

```python
worker = MultiThreadWorker(processor=ExampleProcessor(), book=3)
```

Or start from a specific section and then all its descendants:

```python
worker = MultiThreadWorker(processor=ExampleProcessor(), section=680)
```

Specify how many threads to use:

```python
worker = MultiThreadWorker(processor=ExampleProcessor(),
                           book=4,
                           threads=20)

```

Read a specific version:

```python
worker = MultiThreadWorker(processor=ExampleProcessor(),
                           book=4,
                           source=18)
```

Write the processed texts to a specific version:

```python
worker = MultiThreadWorker(processor=ExampleProcessor(),
                           book=4,
                           target=18)
```

Create a version to save the processed texts:

```python
worker = MultiThreadWorker(processor=ExampleProcessor(),
                           book=4,
                           create=True,
                           name="My New Version")
```

Put everything together:

```python
worker = MultiThreadWorker(processor=ExampleProcessor(),
                           threads=20,
                           book=4,
                           source=6,
                           create=True,
                           name="My New Version")
```

Or maybe

```python
worker = MultiThreadWorker(processor=ExampleProcessor(),
                           threads=20,
                           section=576,
                           source=12,
                           target=20)
```

### <a name="Recipe" style="color: #000;"></a> A Recipe of Multithreaded Text Processing: Removing Digits

```python
import re
import logging

import pdf_client
from pdf_client import config
from pdf_client.multithread.worker import MultiThreadWorker
from pdf_client.multithread.processor import TextProcessor

class MyProcessor(TextProcessor):
	def process(self, text, section_id):
		return re.sub(r'\d+', '', text)
		
def main():
	# enable INFO level logging
	logging.basicConfig()
	logging.getLogger(pdf_client.multithread.worker.__name__).setLevel(logging.INFO)
	
	# load global config
	config.load_from_file('config.json')
	
	worker = MultiThreadWorker(processor=MyProcessor(), book=3, new=True, name="Removed Digits")
	
	completed = worker.start()
	for future in completed:
		section_id, text = future.result()
		# do something else
```
