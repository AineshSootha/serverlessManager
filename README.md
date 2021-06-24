# Serverless Manager

A basic Python Tool that simplifies the deployment of multiple AWS Lambda functions directly from an AWS CodeCommit Repository.

## Set Up

 - Set up an IAM user on your AWS console 
	 - You require the following permissions:
	  ![Permissions for IAM user](/assets/permissions.png)
	 - Store the Access Key ID and the Secret Access Key
	 - Generate the git credentials for the user. (Security Credentials -> HTTPS Git Credentials.
 
 - Create a CodeCommit Repository and clone it to your directory using the Git Credentials.

 - Create a CodeBuild Project
	- Set the source provider to **CodeCommit** and the repository to the newly created CodeCommit repository
	- Pick the branch you will be pushing to.
	- In buildspec, choose **“Use a buildspec file”** and leave the filename empty (Since the default is  **_buildspec.yml_**
	- Create the project
	- Edit the environment variables and add the following variables:
	 ![Environment Variables](/assets/envVariables.png)
	- The ENV_NAME_ variables refer to the different environments you would be deploying. For instance, I have 3 environments: dev, prod and uat. This allows us to deploy the lambda function at different stages (Creating a different function for each stage)

- Create a CodePipeline
	- Source provider:  **_AWS CodeCommit_**
	- Repo Name:  **_Source repo_**
	- Build Provider:  **_AWS_**  **_CodeBuild_**
	- Project Name:  **_Name of Codebuild Project_**
	- Skip deploy stage since we are using the [Serverless Framework](https://www.serverless.com/framework/docs/providers/aws/) to deploy our functions
	- Create the Pipeline
 
- Install serverless-manager and place it in the directory with your handlers

## Using the tool

 - Run serverless manager on your terminal and follow the instructions:
  ![First Steps](/assets/firstSteps.png)
 - Here, I created a service called "CodeCommitTest" and set the AWS-region to us-east-2 (which is what my AWS console is set to). The 
 
