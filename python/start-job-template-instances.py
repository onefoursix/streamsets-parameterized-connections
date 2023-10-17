#!/usr/bin/env python

'''
This script starts one or more Job Template instances on StreamSets Platform based
on values retrieved from a JSON config file

Prerequisites:

 - Python 3.6+; Python 3.9+ preferred

 - StreamSets Platform SDK for Python v6.0.1+
   See: https://docs.streamsets.com/platform-sdk/latest/learn/installation.html

 - StreamSets Platform API Credentials for a user with permissions to start a Job

 - To avoid including API Credentials in the script, export these two environment variables
   prior to running the script:

        export CRED_ID=<your CRED_ID>>
        export CRED_TOKEN=<your CRED_TOKEN>

- Create a config file similar to the JSON files in the config dir 

Run this script passing in the name of the config file, like this:

    $ python start-job-template-instances.py ../config/database-to-adls-properties.json

'''

import datetime, json, os, sys
from streamsets.sdk import ControlHub

# Validate command line args
if len(sys.argv) != 2:
    print('Error: wrong number of arguments')
    print('Usage: $ python start-job-template-instance.py <job-template-instance-properties.json>')
    print('Example: $ python start-job-template-instance.py database-to-adls-properties.json')
    sys.exit(1)

config_file = sys.argv[1]

# Get CRED_ID from the environment
cred_id = os.getenv('CRED_ID')
if cred_id == None:
    print('Error: \'cred_id\' not found in the environment')
    sys.exit(1)

# Get CRED_TOKEN from the environment
cred_token = os.getenv('CRED_TOKEN')
if cred_id == None:
    print('Error: \'cred_token\' not found in the environment')
    sys.exit(1)

# Load the JSON config file
try:

    with open(config_file) as f:

        # Parse the JSON config file
        properties = json.load(f)

        # Get the Job Template ID
        job_template_id = properties['job_template_id']

        # Get the Job Template Instance Name Suffix
        instance_name_suffix = properties['instance_name_suffix']

        # Get parameter name if needed
        if instance_name_suffix == 'PARAM_VALUE':
            parameter_name = properties['parameter_name']
        else:
            parameter_name = None

        # Get the attach_to_template property
        attach_to_template = properties['attach_to_template']

        # Get the delete_after_completion property
        delete_after_completion = properties['delete_after_completion']

        # Get the Runtime Parameters
        runtime_parameters = properties['runtime_parameters']
        if not isinstance(runtime_parameters, list) or len(runtime_parameters) == 0:
            print('Error: runtime_parameters is not a list with at least one element')
            sys.exit(1)

except Exception as e:
    print('Error parsing config file: ' + str(e))
    sys.exit(1)


# Connect to Control Hub
print('Connecting to Control Hub')
sch = ControlHub(
    credential_id=cred_id,
    token=cred_token)

# Find the Job Template
try:
    print('Looking for Job Template with ID \'' + job_template_id + '\'')
    job_template = sch.jobs.get(job_id=job_template_id)
except:
    print('Error: Job Template with ID \'' + job_template_id + '\' not found.')
    sys.exit(1)

print('Found Job Template with name \'' + job_template.job_name + '\'')


# Print the instance parameters
for i in range(0, len(runtime_parameters)):
    print('---')
    print('Runtime Parameters for Job Template Instance ' + str(i) + ':')
    for j in runtime_parameters[i].keys():
        print(j + ':' + str(runtime_parameters[i][j]))
print('---')

# Create and start the Job Template Instance(s)
if len(runtime_parameters) == 1:
    print('Starting 1 Job Template Instance')
else:
    print('Starting ' + str(len(runtime_parameters)) + ' Job Template instances')

job_template_instances = sch.start_job_template(job_template,
                                                instance_name_suffix=instance_name_suffix,
                                                parameter_name = parameter_name,
                                                runtime_parameters=runtime_parameters,
                                                attach_to_template=attach_to_template,
                                                delete_after_completion=delete_after_completion)

print('Done')
