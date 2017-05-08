## RDW_DataGenerator for Developers

**NOTE: recent changes to produce XML output may have broken existing functionality; don't expect the other output 
formats to work without some testing. Yeah, sorry about that but legacy output will be deprecated soon anyway.**

This document is targeted at developers contributing to the RDW_DataGenerator project.


### Version Control Conventions
Repo: https://github.com/SmarterApp/RDW_DataGenerator

This project follows the common convention of having two main branches with infinite lifetime: `master` is the main
branch where HEAD contains the production-ready state, while `develop` is the main branch where HEAD contains the 
latest changes for the next release.
 
Use feature branches off of `develop` for all new features. Use a prefix of `feature/` to highlight those branches.
For example, the new shoesize feature work would be in `feature/shoesize`. Create pull requests from the feature
branch to `develop` to solicit code reviews and feedback. Once approved use `squash and merge` into `develop`.


### How do I get set up?
This is a Python 3 project and as such you will need Python 3 installed to develop the project.
We were using Python 3.3.6 during our development, not sure how much it matters.

To set up a virtual environment, execute the following command:

    virtualenv data-gen-env

> Where `data-gen-env` is the name of the directory where you want your environment files placed. 

You can activate the virtual environment with this command (_note that `data-gen-env` is the same name that was used 
with the creation of the environment. If you change the name of the environment in the first command, change it in 
this command too_):

    source data-gen-env/bin/activate

Once you have your environment activated (or you've decided not to use an environment), go into your repository and run
this command to finish setup:

    python setup.py develop

Note the use of `develop` in the call to `setup.py`. This will create a sym-link from the site-packages directory to the
working directory of your code. If instead you use `install`, it will copy the code and changes you make to the code
will probably not be picked up.

You will need `nose` to run the test suites. Along with those, we are using
[`coverage`](http://nedbatchelder.com/code/coverage/) for a unit testing code coverage report and
[`pep8`](http://pep8.readthedocs.org/en/latest/) as a style checker. If you have a virtual environment, run this within
it:

    pip install nose coverage pep8

Within the project is a suite of unit tests that cover a large percentage of the codebase. We are using `nose` for the
unit tests. To run the unit tests, start from the root of the project and call:

    nosetests test/*

As you develop new functionality, make sure to write accompanying unit tests so as maintain good code coverage and the
confidence that comes with it.


### Build and Push the docker image
Building the docker image is not automated so you must do it manually. Assuming you have Docker installed then, 
from the root folder of the project you can build and push the image:

    docker build -t fwsbac/rdw-datagen:latest .
    docker push fwsbac/rdw-datagen

Refer to README.md for instructions for running the docker image.


### Running

#### Running From IDE
The README outlines how to run the generator using docker. As a developer you will want to run the generator from
the IDE. To run from IntelliJ, from the generate_data.py tab, select `Create 'generate_data'`, set the Script 
Parameters to, for example, `--state_type devel --gen_sum --xml_out`, verify the other settings and run/debug.


### Tasks
This project was originally created to generate data for the legacy reporting data warehouse. It was modified to 
generate data for the new system, mostly to take advantage of the good demographics generation. As such there are a 
number of things that may need cleaning up. And there are some enhancements/improvements. In no particular order:

 - [x] Scores for IAB outcomes
 - [ ] Use only a subset of items from item bank in a particular session outcome (?)
 - [ ] Session-based generation. Assign sessionId, test adminstrator, etc.
 - [ ] Valid categories for IAB are 1 -3, it returns 2-4
 - [ ] ICA report is missing claim scores
 - [ ] Valid categories for IAB are 1 -3, it returns 2-4
 - [ ] date-taken should be passed into outcome generation, not pulled from assessment.
 - [ ] min/max scores are silly (1200/2400, grade independent); should use LOSS/HOSS tables from SB docs. 
 - [ ] How are Section/Staff used? Can they be removed? Consider the session-based generation task.
 - [ ] Combine remaining sbac_generators into generators.
 - [ ] IDGen: remove MTS, clean up in general.
 - [ ] Stage work to avoid memory utilization problems for large generations.
 - [ ] Load District/School configurations to allow multiple generations against the same values.
 - [ ] Make item.max_score more complex than 1; configure some to be unscored (-1). Then percolate to item outcomes,
making score more complex than 0/1.
 - [ ] Make some items field tests (i.e. item.operational='0')
 - [ ] Improve fake answers for items; based on item type of course.
 - [ ] Reuse IAB packages. Currently the system generates multiple IAB packages for a single year, each with a 
 different `period`. It makes more sense to separate the IAB packages from the date taken. So a single IAB package
 might be used more than once during the academic year. Or even in a subsequent academic year. To do this, remove
 `period` from the package; then generate the date-taken and pass it in when generating outcomes.
 - [ ] Clean up accommodations. These belong to the student profile combined with assessment-specific restrictions.
 - [ ] Remove deprecated output workers. Consider that pg_worker could be repurposed as a sql_worker.
 - [ ] Student.skip_iab is not being used. Should it? Some way of skipping IAB's at the student level makes sense.
 