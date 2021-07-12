#! /usr/bin/env python3

import click
from pathlib import Path
from colorama import Fore, init, Style
import boto3
import botocore
import json
import time
from progress.bar import Bar
import os
import glob
import os.path as path
#import importlib
import yaml
#import pprint
from collections import OrderedDict

__VERSION__ = "0.2.2"
init() #colorama

class credentials:
    def __init__(self, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, repoURL=""):
        self.AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
        self.AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY
        self.AWS_DEFAULT_REGION = AWS_DEFAULT_REGION
        self.repoURL = repoURL
    def setRepoURL(self, repoURL):
        self.repoURL = repoURL
    def printRepoURL(self):
        print(f"The HTTP clone URL for the repo: {Fore.YELLOW}{self.repoURL}{Style.RESET_ALL}")



'''AWS Stuff'''
def importToStack(creds, funName):
    slsYML = yaml.load(open("serverless.yml"), yaml.SafeLoader)
    slsService = slsYML['service']
    slsStage = slsYML['provider']['stage']
    stackName = slsService + '-' + slsStage
    funHandler = slsYML['functions'][funName]['handler']
    funRuntime = slsYML['functions'][funName]['runtime']
    actualFunName = slsService + '-' + slsStage + '-' + funName
    funId = funName = funName[0].upper() + funName[1:] + "LambdaFunction"
    try:
        lambda_client = boto3.client('lambda', 
                                    region_name=creds.AWS_DEFAULT_REGION, 
                                    aws_access_key_id=creds.AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY
                                    )
        functionResponse = lambda_client.get_function(
                                FunctionName=actualFunName
                            )
    except:
        print(f"Function {funName} OK. Continuing...\n")
        return
    cf_client = boto3.client('cloudformation', 
                            region_name=creds.AWS_DEFAULT_REGION, 
                            aws_access_key_id=creds.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY
                            )
    try:
        exists_response = cf_client.describe_stacks(
                            StackName=stackName
                        ) 
    except:
        print("SLSMANAGER EXCEPTION\nStack not found. \
              \nThis exception occurs when you are trying to redploy a previously deleted function that still exists. \
              Did you rename the serverless cloudformation stack? \
              If not, submit an issue: https://github.com/AineshSootha/serverlessManager/issues")
    templateDict = dict()
    funCode = dict()
    try:
        print(stackName)
        cf_template = cf_client.get_template(
                StackName=stackName
            )
        
    except:
        print("SLSMANAGER EXCEPTION\nCloudformation Template not found. \
              \nThis exception occurs when you are trying to redploy a previously deleted function that still exists.\n \
              Did you rename the serverless cloudformation stack?\n \
              If not, submit an issue: https://github.com/AineshSootha/serverlessManager/issues", )
    try:
        lambda_client = boto3.client('lambda', 
                                region_name=creds.AWS_DEFAULT_REGION, 
                                aws_access_key_id=creds.AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY
                                )
        functionResponse = lambda_client.get_function(
                                FunctionName=actualFunName
                            )
        funCode = functionResponse['Code']
    except botocore.exceptions.ClientError as error:
        print("SLSMANAGER EXCEPTION\nCloudformation Template not found. \
            \nThis exception occurs when you are trying to redploy a previously deleted function that still exists.\n \
            Did you rename the serverless cloudformation stack?\n \
            If not, submit an issue: https://github.com/AineshSootha/serverlessManager/issues", ) 
        raise(error)  
    
    templateDict = cf_template
    newFunDict = OrderedDict()
    newFunDict =  {
            "Type": "AWS::Lambda::Function",
            "DeletionPolicy": "Retain",
            "Properties": {
                "Code": {
                    "ZipFile":funCode['Location']
                },
                "Handler": funHandler,
                "Runtime": funRuntime,
                "FunctionName": actualFunName,
                "MemorySize": 1024,
                "Timeout": 6,
                "Role": {
                    "Fn::GetAtt": [
                        "IamRoleLambdaExecution",
                        "Arn"
                    ]
                }
            }
        }
    newFunDict = OrderedDict(newFunDict)
    templateDict['TemplateBody']['Resources'][funId] = newFunDict
    #pprint.pprint(templateDict['TemplateBody']['Resources'])
    templateJson = json.dumps(templateDict['TemplateBody'])
    cf_response = cf_client.create_change_set(
                            StackName=stackName,
                            TemplateBody = templateJson,
                            ChangeSetName='import'+'-'+funName,
                            Capabilities=['CAPABILITY_NAMED_IAM'],
                            ClientToken='import'+'-'+funName,
                            Description=f'importing {funName}',
                            ChangeSetType='IMPORT',
                            ResourcesToImport=[
                                {
                                    'ResourceType': 'AWS::Lambda::Function',
                                    'LogicalResourceId': funId,
                                    'ResourceIdentifier': {
                                        'FunctionName': actualFunName
                                    }
                                },
                            ]
                        )
    bar = Bar(f'Readding {funName} to the Cloudformation Template.', max=100)
    for i in range(100):
        time.sleep(0.15)
        bar.next()
    bar.finish()
    changeSet_response = cf_client.execute_change_set(
                            ChangeSetName=f"import-{funName}",
                            StackName=stackName
                        )
    time.sleep(10)

def createRepo(repoName, repoDesc, creds):
    CC_client = boto3.client('codecommit', 
                            region_name=creds.AWS_DEFAULT_REGION, 
                            aws_access_key_id=creds.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY
                            )
    repoCreate_response = CC_client.create_repository(
        repositoryName=repoName,
        repositoryDescription=repoDesc
    )
    creds.setRepoURL(repoCreate_response['repositoryMetadata']['cloneUrlHttp'])


def commitToRepo(repoName,branchName,fName,creds):
    CC_client = boto3.client('codecommit', 
                            region_name=creds.AWS_DEFAULT_REGION, 
                            aws_access_key_id=creds.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY
                            )
    with open("buildspec.yml", "rb") as fin:
        CC_response_bspec = CC_client.put_file(
            repositoryName=repoName,
            branchName=branchName,
            fileContent=fin.read(),
            filePath="buildspec.yml",
            commitMessage='buildSpec.yml',
        )
    with open("buildspec.yml", "rb") as fin:
        CC_response_sls = CC_client.put_file(
            repositoryName=repoName,
            branchName=branchName,
            fileContent=fin.read(),
            filePath="serverless.yml",
            commitMessage='serverless.yml',
        )
    with open(fName, "rb") as fin:
        CC_response = CC_client.put_file(
            repositoryName=repoName,
            branchName=branchName,
            fileContent=fin.read(),
            filePath=fName,
            commitMessage=f"Added {fName}",
        )


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


def addDevAlias(fun, creds):
    lambda_client = boto3.client('lambda', 
                            region_name=creds.AWS_DEFAULT_REGION, 
                            aws_access_key_id=creds.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY
                            )
    try:
        alias_response = lambda_client.get_alias(
                            FunctionName=fun,
                            Name='dev'
                        )
    except:
        create_response = lambda_client.create_alias(
                            FunctionName=fun,
                            Name='dev',
                            FunctionVersion='$LATEST'
                        )
        return create_response
    return alias_response
    
'''Serverless Framework Stuff'''
def updateDeletion():
    slsYML = yaml.load(open("serverless.yml"), yaml.SafeLoader)
    slsFunctions = slsYML['functions']
    with open("serverless.yml", "a") as fSls:
        fSls.write('\n\nresources:\n  extensions:\n')
        for fun in slsFunctions.keys():
            funName = fun[0].upper() + fun[1:] + "LambdaFunction"
            funName = funName.replace('-','Dash')
            funName = funName.replace('_','Underscore')
            slsLine = f"    {funName}:\n      DeletionPolicy: Retain\n"
            fSls.write(slsLine)


def deleteAlias(creds, funName):
    lambda_client = boto3.client('lambda', 
                            region_name=creds.AWS_DEFAULT_REGION, 
                            aws_access_key_id=creds.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=creds.AWS_SECRET_ACCESS_KEY
                            )
    slsYML = yaml.load(open("serverless.yml"), yaml.SafeLoader)
    slsService = slsYML['service']
    slsStage = slsYML['provider']['stage']
    finfunName = slsService + '-' + slsStage + '-' + funName
    lambda_client.delete_alias(
                        FunctionName=finfunName,
                        Name='dev'
                    )
    print(f"Dropping dev alias for {finfunName}")


def createAliases(creds):
    slsYML = yaml.load(open("serverless.yml"), yaml.SafeLoader)
    slsService = slsYML['service']
    slsFunctions = slsYML['functions']
    slsStage = slsYML['provider']['stage']
    for fun in slsFunctions.keys():
        funName = slsService + '-' + slsStage + '-' + fun
        response = addDevAlias(funName,creds)
        if not response:
            exit(1)
       

def makePyModules(py_fileList):
    for pyFile in py_fileList:
        relPath = path.relpath(pyFile)
        module = relPath.split(".")[0] + "." + "lambda_handler"
        funName = relPath.split(".")[0].replace('/', '_')
        funName = funName[:-16]
        addTosls(relPath, module, funName, "python3.7")
        print(module)


def makeJSModules(js_fileList):
    for jsFile in js_fileList:
        relPath = path.relpath(jsFile)
        module = relPath.split(".")[0] + "." + "handler"
        funName = relPath.split(".")[0].replace('/', '_')
        funName = funName[:-6]
        addTosls(relPath, module, funName, "nodejs12.x")


def createSls(service, region, stage = "dev"):
    sls = f'service: {service}\n\nframeworkVersion: \'2\'\n\nprovider:\n  name: aws\n  lambdaHashingVersion: 20201221\n  region: {region}\n  stage: {stage}\n\npackage:\n  individually: true\n\nfunctions:\n'
    with open('serverless.yml', 'w') as fSls:
        fSls.write(sls)
    print(f"{Fore.GREEN}Serverless.yml created{Style.RESET_ALL}")


def addTosls(fname, module, funName, runtime):
    with open('serverless.yml', 'r') as fSls:
        dataLines = fSls.readlines()
        j = 0
        for i in dataLines:
            if 'functions:' in i:
                break
            j += 1
        j += 1
        dataLines.insert(j, f'  {funName}:\n    runtime: {runtime}\n    handler: {module}\n    package:\n      patterns:\n        - \'!./**\'\n        - \'{fname}\'\n')
        
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
        

def addToBSpecList(env_name, allorOne, funNameList):
    if allorOne == 'A' or allorOne == 'a':
        deployCmd = f'      - sls deploy -v -s $ENV_NAME_{env_name}\n'
    else:
        deployCmd = ""
        for funName in funNameList:
            deployCmd = deployCmd + f'      - sls deploy -v -s $ENV_NAME_{env_name} -f {funName}\n'

    fBspecLines = f'version: 0.1\nphases:\n  install:\n    commands:\n      - echo install commands\n      - npm install -g serverless\n  pre_build:\n    commands:\n      - echo No pre build commands yet\n  build:\n    commands:\n      - echo Build Deploy\n{deployCmd}  post_build:\n    commands:\n      - echo post build completed on `date`'
    with open('buildspec.yml', 'w') as fBspec:
        fBspec.writelines(fBspecLines)

'''CLI Stuff'''

def bspecCLI():
    env_name = input(f"ENV_NAME: ")
    allorOne = input(f"Press A if you would like to deploy all lambda functions in repo (N otherwise): ")
    funName = ""
    funNameList = []
    if allorOne.lower() != 'a':
        funName = input("Name of function: ")
        more = input("Would you like to deploy other functions? (Y/N): ")
        funNameList.append(funName)
        while more.lower() == 'y':
            funName = input("Name of function: ")
            funNameList.append(funName)
            more = input("Would you like to deploy other functions? (Y/N): ")
    addToBSpecList(env_name, allorOne, funNameList)


def createslsCLI():
    print(f'{Fore.YELLOW}It seems like serverless.yml doesn\'t exist.\n{Style.RESET_ALL}Creating serverless.yml\n{Fore.YELLOW}For info, Visit: https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml/{Style.RESET_ALL} ')
    service = input('Service Name: ')
    region = input('Region: ')
    stage = input('Stage: ')
    createSls(service, region)


def addCLI():
    slsPath = Path('serverless.yml')
    addorNo = 'y'
    if not slsPath.exists():
        createslsCLI()
        addorNo = input("Would you like to add functions to serverless.yml? (Y/N): ")
    
    if addorNo.lower() == 'y':
        module = input("Name of Module (Eg: handler.firstFun): ")
        funName = input("Name of Function: ")
        fName = module.split('.')[0] + '.js'
        mName = module.split('.')[1]
        fPath = Path(fName)
        print(f"{Fore.GREEN}OK! Adding {module} to serverless.yml{Style.RESET_ALL}\n")
        addTosls(fName, module, funName)
        more = input("Would you like to deploy other functions? (Y/N): ")
        while more.lower() == 'y':
            module = input("Name of Module (Eg: handler.firstFun): ")
            funName = input("Name of Function: ")
            fName = module.split('.')[0] + '.js'
            mName = module.split('.')[1]
            fPath = Path(fName)
            print(f"{Fore.GREEN}OK! Adding {module} to serverless.yml{Style.RESET_ALL}\n")
            addTosls(fName, module, funName)
            more = input("Would you like to deploy other functions? (Y/N): ")
        print(f"If you want to add more properties, \n{Fore.YELLOW}visit: https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml/{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}If you would like to add more files (Other than '{fName}') to the lambda function, edit serverless.yml and add the required files to the \'package\' section under your newly added function.{Style.RESET_ALL}\n")
    openBspec = input("Would you like to create/update Buildspec.yml? (Y/N): ")
    if openBspec.lower() == 'y':
        bspecCLI()


def ccCLI():
    AWS_ACCESS_KEY_ID = input('AWS ACCESS KEY ID: ')
    AWS_SECRET_ACCESS_KEY = input('AWS SECRET ACCESS KEY: ')
    AWS_DEFAULT_REGION = input('AWS DEFAULT REGION: ')
    repoName = input('CodeCommit Repository Name: ')
    repoDesc = input('Repository description (Leave empty if blank): ')
    creds = credentials(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)
    createRepo(repoName, repoDesc, creds)
    creds.printRepoURL()
    return creds


def cbCLI(creds):
    if not creds:
        AWS_ACCESS_KEY_ID = input('AWS ACCESS KEY ID: ')
        AWS_SECRET_ACCESS_KEY = input('AWS SECRET ACCESS KEY: ')
        AWS_DEFAULT_REGION = input('AWS DEFAULT REGION: ')
        repoURL = input('CodeCommit Repository URL: ')
        creds = credentials(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, repoURL)
    projName = input("Name of CodeBuild project: ")
    createCB(projName, creds)
    return creds


def skipCLI(service, region, stage, files=0):
    createSls(service, region, stage)
    if files == 1:
        js_fileList = glob.glob(os.getcwd() + "/**/*.js", recursive=True)
        py_fileList = glob.glob(os.getcwd() + "/**/*.py", recursive=True)
    else:
        js_fileList = glob.glob(os.getcwd() + "/**/index.js", recursive=True)
        py_fileList = glob.glob(os.getcwd() + "/**/lambda_function.py", recursive=True)
    makePyModules(py_fileList)
    makeJSModules(js_fileList)
   
    


@click.command()
@click.option('--nocli', '-n', is_flag=True)
@click.option('--options', '-o', nargs=3, type=str)
@click.option('--buildspec', '-b', is_flag=True)
@click.option('--add', '-a', is_flag=True)
@click.option('--files', '-f', is_flag=True)
@click.option('--alias', '-l', nargs=3, type=str)
@click.option('--delete', '-d', nargs=1, type=str)
@click.option('--updatedeletion', '-u', is_flag=True)
@click.option('--importtostack', '-i', nargs=4)
def main(nocli, options, buildspec, add, files, alias, delete, updatedeletion, importtostack):
    print(f"{Fore.CYAN}========SLS Manager v{__VERSION__}========{Style.RESET_ALL}")
    if(add != 1 and buildspec != 1 and nocli != 1 and not alias and updatedeletion != 1 and not importtostack):
        creds = None
        ccInput = input("Would you like to create a new CodeCommit Repo? (Y/N): ")
        if ccInput.lower() == 'y':
            creds = ccCLI()
        
        cbInput = input("Would you like to create a new CodeBuild project? (Y/N): ")
        if cbInput.lower() == 'y':
            creds = cbCLI(creds)
        
        addCLI()

    elif add == 1:
        addCLI()
   
    elif buildspec == 1:
        bspecCLI()

    elif nocli == 1:
        if not options:
            print("You need to use -o/--options flag with --nocli!")
            return
        service, region, stage = options
        skipCLI(service, region, stage, files)
    elif alias:
        creds = credentials(alias[0],alias[1], alias[2])
        if delete:
            deleteAlias(creds, delete)
        else:
            createAliases(creds)
    elif updatedeletion == 1:
        updateDeletion()
    elif importtostack:
        creds = credentials(importtostack[0],importtostack[1], importtostack[2])
        importToStack(creds, importtostack[3])
        
if __name__ == "__main__":
    main()
