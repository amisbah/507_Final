SI 507 Final Project: Extracting Videos and Podcasts from VOX Media

Purpose: to gather data from VOX Media's video and media content and to compare mediums' topic options

	- this project used BeautifulSoup to capture each url's HTML - therefore, no API keys are necessary
	- this analysis can provide a basis to further explore how Vox decides to explore certain topics based on different mediums. I hypothesize that there may a discrepancy in proportion of topic mentions due to intrinsic restrictions of each medium (video vs. podcasts).

This code requires Python 3 to run. SI507F17_finalproject.py includes code that will gather html, class attributes, and input into Postgres SQL database. SI507F17_finalproject_tests.py will test the code file.

NOTE: SI507F17_finalproject.py includes Selenium package functionality, which will manually scroll through the podcast iframes (5 total iframes, one per podcast show). This will take time to process each time (and will open 5 more windows), but should all run without errors the first time. Just a note, if one plans to run this several times. This applies to running the test file, as well, of course.

Please use the config_example.py file as a template for using the database code (starts on line 213 of the code file)

Before running the files, please install all items in the requirements.txt file.

Summary of code file:

	- Set up caching system functions
	- Set up HTML scraping functions 
		- Use Selenium to capture HTML
	- Set up HTML text mining functions
	- Run HTML functions on video URLs
	- Run HTML functions on podcast URLs
	- Create class definitions
	- Create class instances
		- Class attributes will capture data elements needed for database
	- Create database connection (I used TeamSQL)
	- Create 2 database tables (videos, podcasts)
	- Insert data using class definitions

At the end of the file processing, you should see:

	- Two tables in the database (which you named using the config_example.py as a template)
	- A Plotly visualization that compares keywords between both Vox platforms (use the URL from command line)