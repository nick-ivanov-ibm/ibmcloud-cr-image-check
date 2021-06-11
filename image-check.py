import requests
import os
import sys
import urllib

""" Check image in CR for vulnerabilities and trigger Docker build if found.

Required environment variables:
- APIKEY -- IBM Cloud API key
- CLOUD_ACCT -- IBM Cloud account ID
- IMG_NAME_TAG -- Full name and tag of the docker image to monitor, e.g.
                  "us.icr.io/wh-tor-dev-rns/hdtl-ibmcos-sink:1.1.0"
- DEVOPS_PIPELINE_ID -- devops pipeline ID
- DEVOPS_WEBHOOK_ID -- devops trigger ID. In the example URL https://devops-api.us-east.devops.cloud.ibm.com/v1/tekton-webhook/55c8bed2-2d6c-4dfe-b766-d07eed236418/run/9a820d05-5183-470b-b5ac-01d2cad6b6b7                  
                "55c8bed2-2d6c-4dfe-b766-d07eed236418" is the pipeline ID and
                "9a820d05-5183-470b-b5ac-01d2cad6b6b7" is the trigger ID.
- DEVOPS_WEBHOOK_TOKEN -- authentication token for the webhook. Parameter name will be "token".               
"""

IAM_ENDPOINT="https://iam.cloud.ibm.com/identity/token"
CR_VA_ENDPOINT="https://us.icr.io/va/api/v3"  # Dallas
DEVOPS_ENDPOINT="https://devops-api.us-east.devops.cloud.ibm.com/v1/tekton-webhook"

def main():
    # Obtain IAM token using the API key
    params = {
        'apikey': os.environ['APIKEY'], 'response_type': 'cloud_iam',
        'grant_type': 'urn:ibm:params:oauth:grant-type:apikey'
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    req = requests.post(IAM_ENDPOINT, params=params, headers=headers)
    if req.status_code >= 300:
        print("Unexpected response code {0} from IAM".format(req.status_code), 
              file=sys.stderr)
        sys.exit(-1)
    
    token = req.json()['access_token']

    # Request image status
    params = {'name': os.environ['IMG_NAME_TAG']}
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer {0}".format(token),
        "Account": os.environ['CLOUD_ACCT']
    }
    req = requests.get("{0}/report/image/status/{1}".format(
        CR_VA_ENDPOINT, urllib.parse.quote(os.environ['IMG_NAME_TAG'])), 
        params=params, headers=headers
    )

    if req.status_code >= 300:
        print("Unexpected response code {0} from VA; data: {1}".format(req.status_code, req.json()), 
              file=sys.stderr)
        sys.exit(-1)
    
    resp = req.json()
    print("Image {0}\nConfiguration issues: {1}\nVulnerabilities: {2}".format(
        os.environ['IMG_NAME_TAG'], resp['configuration_issue_count'],
        resp['vulnerability_count']
    ))

    # trigger CI pipeline if vulnerabilities are found
    if resp['vulnerability_count'] > 0:
        headers = {'token': os.environ['DEVOPS_WEBHOOK_TOKEN']}
        req = requests.post(
            "{0}/{1}/run/{2}".format(DEVOPS_ENDPOINT, os.environ['DEVOPS_PIPELINE_ID'], os.environ['DEVOPS_WEBHOOK_ID']),
            headers=headers
        )
    if req.status_code >= 300:
        print("Unexpected response code {0} from DevOps trigger; data: {1}".format(req.status_code, req.json()), 
              file=sys.stderr)
        sys.exit(-1)

    # TODO Add slack notification to re-tag the image if build is successful
    # req.json()['url'] and req.json()['html_url'] will point to the pipeline execution status, might be
    # useful to include in the notification

if __name__ == "__main__":
    main()
