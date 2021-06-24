import click
from pathlib import Path

@click.command()
@click.option('--env', '-e')
@click.option('--module', '-m')
@click.option('--bypass', '-b', is_flag=True)
def main(env, module, bypass):
    fName = module.split('.')[0] + '.js'
    fPath = Path(fName)
    if bypass == 1:
        click.echo("Bypass Checks")
        click.echo("OK! Adding {} to serverless.yml".format(module))
    else:
        if fPath.exists():
            click.echo("OK! Adding {} to serverless.yml".format(module))
            click.echo("If you want to add more properties, \nvisit: https://www.serverless.com/framework/docs/providers/aws/guide/serverless.yml/")
        else:
            click.echo("Path {} does not exist! \nIf you still want to add it, run with -b or --bypass".format(fName))
            return
    
if __name__ == "__main__":
    main()