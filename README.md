# Image Check

This Python script checks if the specified image stored in the IBM Cloud Container Registry has any vulnerabilities detected by the Vulnerability Advisor. If there are any, the script calls a DevOps pipeline webhook that rebuilds the image.

Future work:

- Send a notification if a pipeline has been triggered.
- May be automatically retag the new image with the vulnerable image tag.

Expected environment variables:

- `APIKEY` -- IBM Cloud API key
- `CLOUD_ACCT` -- IBM Cloud account ID
- `IMG_NAME_TAG` -- Full name and tag of the docker image to monitor, e.g.
                  "us.icr.io/wh-tor-dev-rns/hdtl-ibmcos-sink:1.1.0"
- `DEVOPS_PIPELINE_ID` -- devops pipeline ID
- `DEVOPS_WEBHOOK_ID` -- devops trigger ID. In the example URL https://devops-api.us-east.devops.cloud.ibm.com/v1/tekton-webhook/XXXXX/run/YYYYY                  
                "XXXXX" is the pipeline ID and "YYYYY" is the trigger ID.
- `DEVOPS_WEBHOOK_TOKEN` -- authentication token for the webhook. Parameter name will be "token".               

Sample execution:

```
APIKEY="XXX" CLOUD_ACCT=abcxxxx \
IMG_NAME_TAG="us.icr.io/wh-tor-dev-rns/hdtl-ibmcos-sink:1.1.0" \
DEVOPS_PIPELINE_ID=XXXXX DEVOPS_WEBHOOK_ID=YYYYY \
DEVOPS_WEBHOOK_TOKEN=ZZZZZ python3 image-check.py

```
