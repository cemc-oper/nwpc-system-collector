# coding: utf-8
import click

from nwpc_workload_collector.loadleveler.commands import jobs


@click.group()
def cli():
    pass


cli.add_command(jobs.command)


if __name__ == "__main__":
    cli()
