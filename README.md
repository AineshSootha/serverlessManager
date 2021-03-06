
# Serverless Manager
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/AineshSootha/serverlessManager/commits)
[![PyPI version shields.io](https://img.shields.io/pypi/v/slsmanager)](https://pypi.org/project/slsmanager/)
[![PyPI Wheel](https://img.shields.io/pypi/wheel/slsmanager)](https://pypi.org/project/slsmanager/)
[![License](https://img.shields.io/pypi/l/slsmanager)](https://github.com/AineshSootha/serverlessManager/blob/main/LICENSE)\
A basic Python Tool that simplifies the deployment of multiple AWS Lambda functions directly from an AWS CodeCommit Repository.

    pip install slsmanager


This project uses a combination of [Serverless](https://www.serverless.com/) and [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html)
## Set Up

 - Set up an IAM user on your AWS console 
	 - You can find the required permissions here: [assets/IAMpolicy](assets/iamPolicy.json)
	 - These policies are only for reference and should be edited as required (to limit access **especially** with IAM permissions)
	 - Store the Access Key ID and the Secret Access Key
	 - Generate the git credentials for the user. (Security Credentials -> HTTPS Git Credentials)


## Using the tool
## Directly through AWS CodeBuild (> v0.1.7) :
 - Serverless Manager can be directly used from AWS CodeBuild. 
 - Set up the required CodeCommit Repo (This can be done through the AWS Console)
 - Clone the repo to your local directory using Git Credentials
 - Skip the next 2 steps if you have a CodeBuild Project and a CodePipeline set up.
- Create a CodeBuild Project:
- **Skip these steps if you used slsmanager to create the project**
	- Set the source provider to **CodeCommit** and the repository to the newly created CodeCommit repository
	- Pick the branch you will be pushing to (usually this is **main**)
	- In buildspec, choose **“Use a buildspec file”** and leave the filename empty (Since the default is  **_buildspec.yml_**
	- Create the project
	- Edit the environment variables and add the following variables:
	 ![Environment Variables](/assets/envVariables.png)
	- The ENV_NAME_st variable is the stage variable that would be a part of the name of the final Lambda you would be deploying. For instance, I have the **_st** variable set to **lambda** and the **SERVICE_Name** variable set to **BestX**, my final Lambdas will be named **BestX-lambda-funName**
 -  Create a CodePipeline:
	 - Using the AWS console:
	- Source provider:  **_AWS CodeCommit_**
	- Repo Name:  **_Source repo_**
	- Build Provider:  **_AWS_**  **_CodeBuild_**
	- Project Name:  **_Name of Codebuild Project_**
	- Skip deploy stage since we are using the [Serverless Framework](https://www.serverless.com/framework/docs/providers/aws/) to deploy our functions
	- Create the Pipeline
 - Create a ***buildspec.yml*** file using the provided template.
 - Add this ***buildspec.yml*** file to the local repository along with your handlers.
 - For now, the js handlers need to be called ***index.js*** and python handlers need to be called ***lambda_function.py***. Place these handlers in sub-directories in your repo directory. 
 - For instance, my test repo directory looked like this:
 ```
 . 
├── buildspec.yml 
├── backend  
│   └── lambda_function.py   
├── deploy  
│   └── lambda_function.py  
├── testing  
│   └── index.js  
└── ui  
    └── index.js
```
 - Once you commit/push these changes, CodeBuild will automatically run Serverless Manager and create a ***serverless.yml*** file (which will be removed after deployment).
 - It will then call `sls deploy` which will deploy your lambda functions
 - Serverless Manager will also create an alias **dev** for each function and point it to **$LATEST**. You can use this alias and add other aliases to stage development.
 - Read more about aliases [here](https://docs.aws.amazon.com/lambda/latest/dg/configuration-aliases.html)
----
## On your Local Computer (Incomplete):
- If you wish to use slsmanager from your local computer to create projects/repositories:
 - Open a terminal window and navigate to the directory with the handler file. 
- Install serverless-manager on your local machine:
	- `pip install slsmanager`
 - Run serverless manager on your terminal:
	  `slsmanager`
  
#### 1. Creating a CodeCommit Repository
- Follow the instructions to create a CodeCommit Repository and clone it to your directory using the Git Credentials.
- You can also do this from the AWS console.

#### 2. Creating a CodeBuild Project
 - **(OPTION 1: using slsmanager)**
 ![Steps to create a project](/assets/cbproj.png)
	- You can use slsmanager to create a CodeBuild Project.
	- You will need your AWS Access Key ID, your Secret Access Key, the default region and the URL to your CodeCommit Repository
- **(OPTION 2: using AWS console)**
	- Follow the steps provided in the first section of this README

#### 3. Creating the CodePipeline
- Serverless manager doesn't support the creation of a CodePipeline yet. 
- Follow the steps provided in the first section of this README



#### 4. Creating ***serverless.yml*** and ***buildspec.yml*** (INCOMPLETE)
**Please use the provided buildspec.yml template and do not create a serverless.yml file using slsmanager as it is currently incomplete**

 If you have a file called ***handlerFun1.js***, and it contains the function firstFun() which you would like to deploy.
 - Follow the on-screen instructions:
  ![First Steps](/assets/firstSteps.png)
	 - Here, I created a service called "CodeCommitTest" 
	 - I set the AWS-region to us-east-2 (which is what my AWS console is set to). 
	 - The stage sets the serverless *stage* property.
	 - The ENV_NAME is the last part of the ENV_NAME_ environment variables (which we set earlier). This will be reflected in the final name of your function on your console. This property allows us to create multiple  deployed versions of the same lambda function source.
	 - Module name follows the convention ***directory/filename.function***
	 - The **function name** is the name of the final lambda function (and is set in ***serverless.yml***).
	 - By default, the only file added to the current lambda function (That will show up on the console) is the handler file provided in the module name. If you would like to include other files in the final lambda function that is deployed, you may edit the newly generated ***serverless.yml*** and add the required files to the **functions/*your_function*/package/patterns**
	 - You may also edit/add any other properties in ***serverless.yml***
	 - Finally, the tool generates a buildspec.yml file for your function.
		 - If you want to deploy all lambda functions present in ***serverless.yml*** you can press **'a'** in the final step. Otherwise, press **'n'**.
	 - Once you have completed all your steps, you will see 2 new files ***serverless.yml*** (Which lists all the properties required to deploy using the Serverless Framework and ***buildspec.yml*** (Which instructs CodeBuild to deploy the function(s) using the given files and properties.


----
 ## Options
- There are a few config options you can use while running **slsmanager**
### Add / Create
   `slsmanager --add/-a` 
   
   - This allows you to skip the preliminary steps in the CLI (Create CodeCommit Repo/ Create CodeBuild Project) and jump directly to adding functions to ***serverless.yml*** and (later) ***buildspec.yml***.

### Buildspec
`slsmanager --buildspec / -b`
	
 - This allows you to skip all preliminary steps in the CLI and jump directly to adding deploy commands to ***buildspec.yml***.

### NoCLI
`slsmanager --nocli/-n`

- **REQUIRES** `-o` to also be used
- This allows you to deploy the functions directly from codeCommit without needing to create a ***serverless.yml***. Follow the steps above.

### Options
`slsmanager -n -o "service" "region" "stage"`

- Options required for the noCLI method.

### Aliases

`slsmanager -l "ACCESS-KEY-ID" "SECRET-ACCESS-KEY" "region"`

- Creates a ***dev*** alias for all functions in the ***serverless.yml*** file.
- This is also run when you use the provided template ***buildspec.yml***
----
