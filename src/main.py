import asyncio
import click
from pathlib import Path
# EmailRewriter module to be implemented
from services import EmailService  # Use the same service
import os


@click.command()
@click.argument("email", type=click.Path(exists=True))(exists=True))
@click.argument('job', type=click.Path(exists=True))
@click.option('--tone', '-t',
              type=click.Choice(['professional', 'casual', 'academic']),
              default='professional')
async def main(email, context, tone):
    """Email rewriting CLI tool."""
    # Use the same service layer as API
    service = EmailService()

    try:
        result = await service.rewrite_email(
            email_text=Path(email).read_text(),
            target_audience=Path(context).read_text(),
            tone=tone
        )
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == "__main__":
    asyncio.run(main())
