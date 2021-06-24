import click
from pathlib import Path
from colorama import Fore, init, Style

init()
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
        dataLines.insert(j, f'  {funName}:\n    handler: {module}\n    package:\n      patterns:\n        - \'!./**\'\n        - \'{fname}\'\n    events:\n      - http:\n        path: test\n        method: get\n')
        
    with open('serverless.yml', 'w') as fSls:    
        dataFinal = "".join(dataLines) 
        fSls.write(dataFinal)

  
def addToBSpec(env_name):
    fBspecLines = f'version: 0.1\nphases:\n  install:\n    commands:\n      - echo install commands\n      - npm install -g serverless\n  pre_build:\n    commands:\n      - echo No pre build commands yet\n  build:\n    commands:\n      - echo Build Deploy\n      - sls deploy -v -s $ENV_NAME_{env_name}\n  post_build:\n    commands:\n      - echo post build completed on `date`'
    with open('buildspec.yml', 'w') as fBspec:
        fBspec.writelines(fBspecLines)
        

@click.command()
@click.option('--skip', '-s', is_flag=True)
@click.option('--buildspec', '-b')
def main(skip, buildspec):

    slsPath = Path('serverless.yml')
    if not slsPath.exists():
        createSls(slsPath)

    env_name = input(f"\nENV_NAME: ")
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
    print(f"{Fore.YELLOW}If you would like to add more files (Other than \'{fName}\') to the lambda function, edit serverless.yml and add the required files to the \'package\' section under your newly added function.{Style.RESET_ALL}\n")
    print(f"{Fore.GREEN}Adding {env_name} to buildspec.yml.{Style.RESET_ALL} \nCheck Environment Variable config here: LINK")
    addToBSpec(env_name)
    





if __name__ == "__main__":
    main()
