# Serverless Manager

A basic Python Tool that simplifies the deployment of multiple AWS Lambda functions directly from an AWS CodeCommit Repository.

## Set Up

 - Set up an IAM user on your AWS console 
	 - With the following permissions:
	 - ![Permissions for IAM user](/assets/permissions.png)
	 - Store the Access Key ID and the Secret Access Key
	 - Generate the git credentials for the user. (Security Credentials -> HTTPS Git Credentials.
 
 - Create a CodeCommit Repository and clone it to your directory using the Git Credentials.

 - Create a CodeBuild Project
	- Set the source provider to **CodeCommit** and the repository to the newly created CodeCommit repository
	- Pick the branch you will be pushing to.
	- In buildspec, choose **“Use a buildspec file”** and leave the filename empty (Since the default is  **_buildspec.yml_**
	- Create the project
	- Edit the environment variables and add the following variables:
	- ![Environment Variables](/assets/envVariables.png)
 - Install serverless-manager and place it in the directory with your handlers
 - Run serverless manager on your terminal and follow the instructions:
 - ![First Steps](/assets/firstSteps.png)
 - Here, I created a service called "CodeCommitTest" and set the AWS-region to us-east-2 (which is what my AWS console is set to) 
 
