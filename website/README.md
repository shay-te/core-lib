# Getting Started with Create React App

## Staring the web application

Run the following commands to start the web application.

```bash
cd core-lib/website
npm start
```

And the application will be visible on port `3000`, if you want to take advantage of exporting zip files from the application you can start the flask server which will generate the `Core-lib` zip file for you.

## Starting the Flask server

You'll find a file named `generator_server.py` under the `website` directory.
This is responsible for starting the flask server which provides APIs for generating and downloading a `Core-lib` zip file.

To start the server use the following commands:

```bash
python website/generator_server.py # from root core-lib folder 
```
