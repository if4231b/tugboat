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

In another terminal do

    $ source python/bin/activate
    $ cd tugboat/static
    $ python -m SimpleHTTPServer
    

## To see identified articles redirect to BBB go to :

Either from browser go to

    http://localhost:8000/index.html

or curl

    curl -X POST 'http://localhost:8000/redirect --data '["bib1", "bib2", "bib3", ...., "bibN"]'

which returns

    {'redirect': 'https://ui.adsabs.harvard.edu/#search/q=*%3A*&__qid=945gfd9gfda9d'}, 200
    
## To see classic query converted and get redirected to BBB go to URL:

    http://localhost:8000/fielded_classic_w_BBB_button.html
    
### Classic Search Redirection Status
Currently, about 20 search parameters from classic are translated to ads bumblebee and an http redirect is returned.
ADS Bumblebee query can include new parameters whose values are human readable descriptions of translation issues.
The new parameters are: error_message, warning_message and unprocessed_parameter.  error_message is used when the
translated search will generate substantially different search results.  Since ADS Bumblebee URL does not
currently support pagination, classic queries with nr_to_return or start_nr will translate to a url with an error_message.
Warming_message is used when search results are useful, but some non-trivial error is present.  For example, if classic
provides an invalid enumerated valued for the database field a warning is generated.  Finally, unprocessed_parameter
lists the parameters that were not translated.  Depending on the specific parameter, this may or may not be critical.
    
## Testing

On your desktop run:

    $ py.test


## Maintainers

Steve, Golnaz
