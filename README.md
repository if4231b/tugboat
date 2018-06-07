[![Build Status](https://travis-ci.org/adsabs/tugboat.svg?branch=master)](https://travis-ci.org/adsabs/tugboat)
[![Coverage Status](https://coveralls.io/repos/github/adsabs/tugboat/badge.svg?branch=master)](https://coveralls.io/github/adsabs/tugboat?branch=master)


# Tugboat Web Service

## Short Summary

* Exports selected articles to ADS Bumblebee.
* Translates classic query and redirects to ADS Bumblebee.



## Setup (recommended)

In one terminal do

    $ virtualenv python
    $ source python/bin/activate
    $ pip install -r requirements.txt
    $ pip install -r dev-requirements.txt
    $ vim local_config.py # edit, edit
    $ python wsgi.py

 
## To see identified articles redirect to BBB go to :

Either from browser go to

    http://localhost:5000/index

or curl for example,

    curl -X POST 'http://localhost:5000/redirect' --data '["1989LNP...329..191A", "1989daa..conf..245A"]'
    
which returns

    {"redirect": "https://devui.adsabs.harvard.edu/#search/q=*%3A*&__qid=de4b6d378395eba013f86454c44659b6"}, 200

    
## To see classic query converted and get redirected to BBB go to URL:

    http://localhost:5000/adsabs
    
### Classic Search Redirection Status
Currently, most of search parameters from classic are translated to ads bumblebee and an http redirect is returned.
ADS Bumblebee query can include new parameters whose values are human readable descriptions of translation issues.
The new parameters are: error_message, warning_message and unprocessed_parameter.  error_message is used when the
translated search will generate substantially different search results.  Since ADS Bumblebee URL does not
currently support pagination, classic queries with nr_to_return or start_nr will translate to a url with an error_message.
Warming_message is used when search results are useful, but some non-trivial error is present.  For example, if classic
provides an invalid enumerated valued for the database field a warning is generated.  Finally, unprocessed_parameter
lists the parameters that were not translated.  Depending on the specific parameter, this may or may not be critical.
 
    
## Testing

On your desktop, before running tests, need to install Chrome and Firefox drivers:

    wget http://chromedriver.storage.googleapis.com/2.21/chromedriver_linux64.zip
    unzip chromedriver_linux64.zip
    sudo chmod u+x chromedriver
    sudo mv chromedriver /usr/local/bin/
    
    wget https://github.com/mozilla/geckodriver/releases/download/v0.20.0/geckodriver-v0.20.0-linux64.tar.gz
    tar -xvzf geckodriver-v0.20.0-linux64.tar.gz
    sudo chmod u+x geckodriver
    sudo mv geckodriver /usr/local/bin/

    $ py.test


## Maintainers

Steve, Golnaz
