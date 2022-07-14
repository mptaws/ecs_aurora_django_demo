
# Django ECS Application Demo

<img src="ECS-Aurora-Serverless.png" width=800 height=600 />

The `cdk.json` file tells the CDK Toolkit how to execute your app.

## Prerequisites

* NodeJS v14 or later
* Python v3.7 or later
* Docker Desktop installed and running locally
* AWS CDK v2 installed `npm install -g aws-cdk`
* If you have never used CDK before, run `cdk bootstrap`
* Git v2 or later
* AWS CLI 2.7 or later with account ID and secret key configured `aws configure`

## After cloning the repository, go into the repo folder

* Create a virtual environment: `python3 -m venv .venv`
* Activate the virtual environment `source .venv/bin/activate`
* Install requirements: `pip install -r requirements.txt`
* Run `cdk synth`
* To deploy the Django app `cdk deploy --all`
