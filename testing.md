# Unit Tests
All unit tests are in the "/tests" directory in their respective files. Unit test coverage is explained in the below sections. In short, any backend procedure is tested in the unit tests while front end interactions are tested via the front end (and are not covered in the unit tests).

## AIQuery
All of these tests create mocks to simulate API calls.

### Test get_response Returns expected Message
Checks to make sure the AI query returns the expected message when prompted.

### Test get_relevant_document
Tests to make sure the prompt is returned correctly.

## Course Parse
### Test parse course info success
Checks that the parse function correctly formats the scraped course information. This tests to make sure the program correctly handles correct input.

### Test parse course info failure
Checks that the parse function correctly handles errors on an invalid input.

## Database Test
These tests create mocks to simulate interactions with the database.

### Test print_length_of_docs
This tests that the loader defaults to 3 returned documents

## Embeddings
### Test embedding output type: single
Tests if the input type is a single string that the returned value is a single embedding (correctly formatted).

### Test embedding output type: list
Tests if the input type is a list of strings that the returned value is a list of embeddings (correctly formatted).

## Parse
These tests use a dummy with dummy data for the testing.

### Test df loaded
Checks that the database is successfully loaded with course information. 

### Test extract prereqs
Checks that the database correctly stores prereqs for courses.

### Test add info
Checks that adding new info to the database occurs correctly.

## Scrape All
### test scrapeall
Tests to make sure that the scraped courses is as expected


## Script
### Test script
Tests that the scraper correctly scrapes information accross a list of links.
