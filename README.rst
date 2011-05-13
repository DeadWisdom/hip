===============
Hip
===============

This is a Flask + Redis project skeleton, and philosophy.

The idea here is to separate out web from api.  So when you create a project
there will be a "web" directory, and another directory will function as your
api, and will be the name of your project.


Organization
===============
The challenge: Never have database / file handling / or anything that effects
state or reads the state of your application in the "web" directory; and never
have anything to do with the "web", like request objects or session objects
in your api directory.

Also, try not to use OOP for objects in your API.  Rather use ids of objects
and data stored in Redis to make very simple functions that perform atomic
operations.

Use the "schema" module to filter the data of your objects.

Implement REST api's where available.

Test your api first, the web second.


UI
===============
Use CleverCSS.

Use jQuery and Tea to make awesome javascript UIs.


Data Storage
===============
Setup Redis to use journaling so that your data is persistent.

Don't implement search functionality in Redis unless you are doing simple
indexing.  Rather add Whoosh or Solr.  Store objects in Redis, and index with
your search engine.


Commands
===============
Use `./create-project.py <project-name>` to create a project.

Edit the template/ directory if you want to make your own project starting
point.
