[![PyPI](https://img.shields.io/pypi/v/core-lib)](https://pypi.org/project/core-lib/)
![PyPI - License](https://img.shields.io/pypi/l/core-lib)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/core-lib)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/core-lib.svg)](https://pypistats.org/packages/core-lib)

# Core-Lib
CoreLib provides basic simple classes for creating a WEB Application as a Library using the Onion Architecture. [1](https://www.codeguru.com/csharp/csharp/cs_misc/designtechniques/understanding-onion-architecture.html) [2](https://www.google.com/search?sxsrf=ACYBGNT0NhYbUZLnDQbC9b6uPBqjZmjwgw%3A1579104811273&ei=KzofXuOfEO3IgwfngLPwAg&q=onion+Architecture&oq=onion+Architecture&gs_l=psy-ab.12...0.0..109691...0.0..0.0.0.......0......gws-wiz.oEYi3afxy_c&ved=0ahUKEwij4drq_4XnAhVt5OAKHWfADC4Q4dUDCAs)   

Check the [website](https://core-lib.netlify.com/) for more information

## License
Core-Lib in licenced under [MIT](https://github.com/shay-te/core-lib/blob/master/LICENSE)

# Starting the Flask server

You'll find a file named `generator_server.py` under the `website` directory.
This is responsible for starting the flask server which provides APIs for generating and downloading a `Core-lib` zip file.

To start the server use the following commands:
```
python website/generator_server.py # from root folder or
python generator_server.py # from website folder
```

# Running tests
`python -m unittest discover -v`
