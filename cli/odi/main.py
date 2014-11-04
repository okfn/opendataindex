import subprocess
import click
from . import utilities
import lib


@click.group()
def cli():
    """CLI entry point."""


@cli.command()
def serve():
    """Run the development server."""

    config = utilities.get_config()

    click.echo('Serving the site now on // NOT IMPLEMENTED')


@cli.command()
def test():
    """Run the project tests."""

    config = utilities.get_config()

    click.echo('Running tests and a coverage report. // NOT IMPLEMENTED')

    # suite = unittest.loader.TestLoader().discover(config['test_path'])
    # runner = unittest.TextTestRunner(verbosity=2)
    # cover = coverage.coverage()
    # cover.start()
    # runner.run(suite)
    # cover.stop()
    # cover.report()


@cli.command()
def deploy():
    """Run the code deployment flow."""

    config = utilities.get_config()

    click.echo('Deploying the code now')

    _generate = ['pelican', config['content_path'], '-o',
                 config['output_path'], '-s', 'config_deploy.py']
    _copy = ['ghp-import', config['output_path']]
    _push = ['git', 'push', config['deploy_remote'], 'gh-pages', '--force']

    click.echo('Generating the static site')
    subprocess.call(_generate)
    click.echo('Copying the generated site to the gh-pages branch')
    subprocess.call(_copy)
    click.echo('Pushing gh-pages branch to the deploy remote')
    subprocess.call(_push)


@cli.command()
@click.argument('action')
def trans(action):
    """Run various translation tasks."""

    actions = ('init', 'extract', 'compile', 'update')

    if not action in actions:
        click.echo('Received an invalid action argument')
        raise ValueError

    config = utilities.get_config()

    _init = ['pybabel', 'init', '-i',
             '{}/messages.pot'.format(config['trans_path']), '-d',
             config['trans_path'], '-l', 'en']
    _extract = ['pybabel', 'extract', '-F', 'babel.config', '-k',
                'lazy_gettext', '-o',
                '{0}/messages.pot'.format(config['trans_path']), '.']
    _compile = ['pybabel', 'compile', '-d', config['trans_path']]
    _update = ['pybabel', 'update', '-i',
               '{0}/messages.pot'.format(config['trans_path']), '-d',
               config['trans_path']]

    if action == 'init':
        subprocess.call(_init)

    if action == 'extract':
        subprocess.call(_extract)

    if action == 'update':
        subprocess.call(_update)

    if action == 'compile':
        subprocess.call(_compile)

@cli.command()
@click.option('--limited', is_flag=True)
def populate(limited):
    """Run the source data population flow.

    By default, only populates au and timetables, to speed up development.

    """

    config = utilities.get_config()

    click.echo('Populating the content source files from data.')
    if limited:
        lib.populate.run(limited_places=config['limited']['places'],
                         limited_datasets=config['limited']['datasets'])
    else:
        lib.populate.run()


if __name__ == '__main__':
    cli()
