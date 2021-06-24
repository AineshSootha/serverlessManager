import click
from pathlib import Path
from colorama import Fore, init, Style


init()

def addTosls(module, funName):
    with open('serverless.yml', 'r') as fSls:
        dataLines = fSls.readlines()
        j = 0
        for i in dataLines:
            if 'functions:' in i:
                break
            j += 1
        j += 1
        dataLines.insert(j, f'  {funName}:\n    handler: {module}\n    events:\n      - http:\n        path: test\n        method: get\n')
        
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
    
    
    addTosls(module, funName)
    print(f"If you want to add more properties, \n{Fore.YELLOW}visit: https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml/{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Adding {env_name} to buildspec.yml.{Style.RESET_ALL} \nCheck Environment Variable config here: LINK")
    addToBSpec(env_name)






if __name__ == "__main__":
    main()
