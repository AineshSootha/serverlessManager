#! /usr/bin/env python3

import click
from pathlib import Path
from colorama import Fore, init, Style
import boto3
import json
import time
from progress.bar import Bar
import importlib
import os

init() #colorama

class credentials:
    def __init__(self, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, repoURL):
        self.AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
        self.AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY
        self.AWS_DEFAULT_REGION = AWS_DEFAULT_REGION
        self.repo_URL = repoURL


def createCBRole(projName, creds):
    IAM_client = boto3.client('iam', 
                            region_name=creds.AWS_DEFAULT_REGION, 
                            aws_access_key_id=creds.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY
                            )
    dataCreate = {
    "Version": "2012-10-17",
    "Statement": [
        {
        "Effect": "Allow",
        "Principal": {
            "Service": "codebuild.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
        }
    ]
    }
    
    dataPut = {
        "Version": "2012-10-17",
        "Statement": [
            {
            "Sid": "CloudWatchLogsPolicy",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "*"
            ]
            },
            {
            "Sid": "CodeCommitPolicy",
            "Effect": "Allow",
            "Action": [
                "codecommit:GitPull"
            ],
            "Resource": [
                "*"
            ]
            },
            {
            "Sid": "S3GetObjectPolicy",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:GetObjectVersion"
            ],
            "Resource": [
                "*"
            ]
            },
            {
            "Sid": "S3PutObjectPolicy",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": [
                "*"
            ]
            },
            {
            "Sid": "S3BucketIdentity",
            "Effect": "Allow",
            "Action": [
                "s3:GetBucketAcl",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "*"
            ]
            }
        ]
    }
    
    IAMPolicy_response = IAM_client.create_policy(
        PolicyName=f'CodebuildBasePolicy-{projName}-role-policy',
        PolicyDocument=json.dumps(dataPut),
    ) 
    #try:
    IAMCreate_response = IAM_client.create_role(
        Path='/service-role/',
        RoleName=f'codebuild-{projName}-service-role',
        AssumeRolePolicyDocument=json.dumps(dataCreate),
        MaxSessionDuration=3600,
    )
    #except Exception:
    #    pass
    #try:
     
    #except Exception:
    #    pass
    #try:
    IAMPut_response = IAM_client.put_role_policy(
        RoleName=f'codebuild-{projName}-service-role',
        PolicyName=f'CodebuildBasePolicy-{projName}-role-policy',
        PolicyDocument=json.dumps(dataPut)
    )
    #except Exception:
    #    pass
    return IAMCreate_response['Role']['Arn']




def createCB(projName, creds):

    ARN = createCBRole(projName, creds) #THIS IS THE MAIN ISSUE. it seems like AWS takes a bit of time to load the roles
    bar = Bar('Processing', max=100)
    for i in range(100):
        time.sleep(0.15)
        bar.next()
    bar.finish()


    CB_client = boto3.client('codebuild', 
                            region_name=creds.AWS_DEFAULT_REGION, 
                            aws_access_key_id=creds.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY
                            )
    CB_response = CB_client.create_project(
        name=projName,
        source={
            'type': 'CODECOMMIT',
            'location': creds.repoURL
        },
        artifacts={
            'type': 'NO_ARTIFACTS'
        },
        environment={
            'type': 'LINUX_CONTAINER',
            'image': 'aws/codebuild/standard:5.0',
            'computeType': 'BUILD_GENERAL1_SMALL',
            'environmentVariables': [
                {
                    'name': 'ENV_NAME_dev',
                    'value': 'dev',
                    'type': 'PLAINTEXT'
                },
                {
                    'name': 'ENV_NAME_prod',
                    'value': 'prod',
                    'type': 'PLAINTEXT'
                },
                {
                    'name': 'ENV_NAME_uat',
                    'value': 'uat',
                    'type': 'PLAINTEXT'
                },
                {
                    'name': 'AWS_DEFAULT_REGION',
                    'value': creds.AWS_DEFAULT_REGION,
                    'type': 'PLAINTEXT'
                },
                {
                    'name': 'AWS_ACCESS_KEY_ID',
                    'value': creds.AWS_ACCESS_KEY_ID,
                    'type': 'PLAINTEXT'
                },
                {
                    'name': 'AWS_SECRET_ACCESS_KEY',
                    'value': creds.AWS_SECRET_ACCESS_KEY,
                    'type': 'PLAINTEXT'
                }
            ]
        },
        serviceRole = ARN,
        timeoutInMinutes=60,
        queuedTimeoutInMinutes=480,
        badgeEnabled=False,
        logsConfig={
            'cloudWatchLogs': {
                'status': 'ENABLED',
                'groupName': 'string',
                'streamName': 'string'
            },
            's3Logs': {
                'status': 'DISABLED'
            }
        }
    )


def createSls(slsPath):
    print(f'{Fore.YELLOW}It seems like serverless.yml doesn\'t exist.\n{Style.RESET_ALL}Creating serverless.yml\n{Fore.YELLOW}For info, Visit: https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml/{Style.RESET_ALL} ')
    service = input('Service Name: ')
    region = input('Region: ')
    stage = input('Stage: ')
    sls = f'service: {service}\n\nframeworkVersion: \'2\'\n\nprovider:\n  name: aws\n  runtime: nodejs12.x\n  lambdaHashingVersion: 20201221\n  stage: {stage}\n  region: {region}\npackage:\n  individually: true\n\nfunctions:\n'
    with open('serverless.yml', 'w') as fSls:
        fSls.write(sls)
        
        
def addTosls(fname, module, funName):
    with open('serverless.yml', 'r') as fSls:
        dataLines = fSls.readlines()
        j = 0
        for i in dataLines:
            if 'functions:' in i:
                break
            j += 1
        j += 1
        dataLines.insert(j, f'  {funName}:\n    handler: {module}\n    package:\n      patterns:\n        - \'!./**\'\n        - \'{fname}\'\n    events:\n      - http:\n          path: test/{funName}\n        method: get\n')
        
    with open('serverless.yml', 'w') as fSls:    
        dataFinal = "".join(dataLines) 
        fSls.write(dataFinal)

  
def addToBSpec(env_name, allorOne, funName):
    deployCmd = f'sls deploy -v -s $ENV_NAME_{env_name} -f {funName}'
    if allorOne == 'A' or allorOne == 'a':
        deployCmd = f'sls deploy -v -s $ENV_NAME_{env_name}'

    fBspecLines = f'version: 0.1\nphases:\n  install:\n    commands:\n      - echo install commands\n      - npm install -g serverless\n  pre_build:\n    commands:\n      - echo No pre build commands yet\n  build:\n    commands:\n      - echo Build Deploy\n      - {deployCmd}\n  post_build:\n    commands:\n      - echo post build completed on `date`'
    with open('buildspec.yml', 'w') as fBspec:
        fBspec.writelines(fBspecLines)
        

@click.command()
@click.option('--skip', '-s', is_flag=True)
@click.option('--buildspec', '-b')
def main(skip, buildspec):
    print(f"{Fore.CYAN}========SLS Manager v 0.1.0========{Style.RESET_ALL}")
    cbInput = input("Would you like to create a CodeBuild project? (Y/N): ")
    if cbInput.lower() == 'y':
        AWS_ACCESS_KEY_ID = input('AWS ACCESS KEY ID: ')
        AWS_SECRET_ACCESS_KEY = input('AWS SECRET ACCESS KEY: ')
        AWS_DEFAULT_REGION = input('AWS DEFAULT REGION: ')
        repoURL = input('CodeCommit Repository URL: ')
        creds = credentials(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, repoURL)
        projName = input("Name of CodeBuild project: ")
        createCB(projName, creds)
    slsPath = Path('serverless.yml')
    if not slsPath.exists():
        createSls(slsPath)
    env_name = input(f"ENV_NAME: ")
    module = input("Name of Module (Eg: handler.firstFun): ")
    funName = input("Name of Function: ")
    fName = module.split('.')[0] + '.js'
    mName = module.split('.')[1]
    fPath = Path(fName)
    if skip == 1:
        print(f"{Fore.YELLOW}Skipping Checks")
        print(f"{Fore.GREEN}OK! Adding {module} to serverless.yml{Style.RESET_ALL}\n")
    else:
        if fPath.exists():
            with open(fName) as fin:
                if mName not in fin.read():
                    print(f"{Fore.RED}Module {mName} Not found in {fName}! \n{Fore.YELLOW}Please check the name or run with -s/--skip.{Style.RESET_ALL}")
                    return
                else:    
                    print(f"{Fore.GREEN}OK! Adding {module} to serverless.yml\n{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Path {fName} does not exist! \n{Fore.YELLOW}If you still want to add it, run program with -s or --skip{Style.RESET_ALL}")
            return
    
    
    addTosls(fName, module, funName)
    print(f"If you want to add more properties, \n{Fore.YELLOW}visit: https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml/{Style.RESET_ALL}\n")
    print(f"{Fore.YELLOW}If you would like to add more files (Other than '{fName}') to the lambda function, edit serverless.yml and add the required files to the \'package\' section under your newly added function.{Style.RESET_ALL}\n")
    print(f"{Fore.GREEN}Adding {env_name} to buildspec.yml.{Style.RESET_ALL} \nCheck Environment Variable config here: LINK")
    allorOne = input(f"Press A if you would like to deploy all lambda functions in repo (N otherwise): ")
    addToBSpec(env_name, allorOne, funName)
    





if __name__ == "__main__":
    main()
