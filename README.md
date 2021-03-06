## README

This project generates sample data to be used in SBAC RDW project for functional testing.

### How do I run it?

There are two scripts you can choose to run. See CONTRIBUTING.md for instructions for running them directly. 
Otherwise use the docker image to run the generate script.

First script is `generate_data.py`. This generates the data in the requested output formats (can generate multiple formats at once).

> The following arguments apply:
> * `--state_name STATE_NAME`: Specify the name of the state that gets generated (defaults to `California`)
> * `--state_code STATE_CODE`: Specify the code of the state that gets generated (defaults to `CA`)
> * `--state_type STATE_TYPE`: Specify the hierarchy type for the state to generate. 
This has to match configuration in in datagen/config/state_type.py. Examples include `california`, `example` and `devel`.

> An alternative to specifying state specs and generating the hierarchy is to load the hierarchy (see test data for format):
> * `--hier_source FILE_NAME`: Specify the source file for the hierarchy

> Select what should be generated and output:
> * `--subject_source`: glob path where subject definition XML files are located, or `generate` to use SBAC default Math and ELA
> * `--pkg_source`: glob path where tabulator CSV files are located
> * `--gen_sum`: generate SUM outcomes
> * `--gen_ica`: generate ICA outcomes
> * `--gen_iab`: generate IAB outcomes
> * `--gen_item`: generate item level data (applies to both packages and outcomes)

> Select desired output:
> * `--xml_out`: Output data to (TRT) XML (defaults to True)

The second script is `calculate_state_size.py`.
This will print out all the configured 'state_type's (from datagen/state_type.py) and the stats for them.
Current output looks like:
```text
Calculating for type: devel
    Districts: 4
    Schools  : 24
    Students : 8600
Calculating for type: udl_test
    Districts: 1
    Schools  : 200
    Students : 200000
Calculating for type: pa
    Districts: 102
    Schools  : 5184
    Students : 2017200
Calculating for type: tiny
    Districts: 2
    Schools  : 12
    Students : 182
Calculating for type: example
    Districts: 13
    Schools  : 264
    Students : 109475
Calculating for type: california
    Districts: 1011
    Schools  : 16150
    Students : 7033000
```
The number of test results produced depends on the distribution of the students, which assessment types are enabled
and which years results are generated for. Using the default 2015, 2016, 2017 you can expect per student, about:
```text
SUM - 6 
ICA - 18
IAB - 147, weighted average of ~130 for grades 3-8, ~230 for grade 11
```
Call it 170 per student over the three years. So, `example` produces > 18 million results; `california` > 1.2 billion! 

Obviously, the size of the output depends on the format:
* XML with item data ~ 18k per file

### Running the docker image
When running the image, pass the data generation parameters, e.g. `--state_type tiny --gen_ica --gen_iab --gen_item --xml_out`.
To provide data (assessment package, organization, etc.) you need to map a local folder and set source parameters, 
e.g. `-v ~/local-in:/in --pkg_source /in`.
To get at the resulting data you need to map a local folder, e.g. `-v ~/local-out:/out`.
Combining all these looks something like:
```
docker run -v ~/out:/out -v ~/in:/in fwsbac/rdw-datagen --state_type tiny --gen_ica --gen_iab --gen_item --xml_out --pkg_source /in/*.csv
```

Perhaps a bit simpler is to have a datagen folder with just what you need and map both `in` and `out` to it:
```
mkdir ~/datagen
cp /where/ever/it/is/2018.Math.csv ~/datagen
docker run -v ~/datagen:/out -v ~/datagen:/in fwsbac/rdw-datagen --hier_source /in/pern.csv --gen_sum --xml_out --pkg_source /in/20*.csv
ls -al ~/datagen
```

#### Setting up an EC2 instance with docker
Followed the directions from: http://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html.
Create EC2 instance using Amazon Linux or CentOS image. Then ...

    sudo yum update -y
    sudo yum install -y docker
    sudo service docker start
    sudo usermod -a -G docker ec2-user     <-- have to relog to be in group
    docker info
    mkdir out
    docker run -v ~/out:/out fwsbac/rdw-datagen --state_type tiny --gen_ica --gen_iab --gen_item --xml_out


#### Update the student responses for EQ, MI, TI, HTQ items
The generator has been modified to provide student responses for these item types (based on the config file in https://github.com/SmarterApp/AP_ItemMaintenanceTools/tree/master/RemediateTrtItemResponse). 
Currently this is for practice items only (many are based on the actual item key); it will have to be made to work for operational items too at some point. And perhaps it could be driven by a configuration file or even modified tabulator output to make updates easier.

### Data Sets
Two generated data set inputs have been preserved for posterity:
* sb-dataset.zip
* ca-dataset.zip
The zip files contain the input that was used to generate the test results.
For sb-dataset, the output is also included in the zip file. The zip files
are password protected, you'll need to get that from somebody who knows.
