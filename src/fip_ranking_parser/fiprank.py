import csv
from pathlib import Path

import click
import pandas as pd
import pypdf
from camelot.io import read_pdf

from .helpers import csv_finder,manual_replace

ranking_original = Path("ranking.csv")
ranking_clean = Path("ranking_clean.csv")

@click.group()
def cli():
    """A tool to parse FIP ranking data from published PDFs \n
    The PDF can be downloaded at https://www.padelfip.com/ranking-male/"""


@cli.command()
# TODO (karl): Change to click file-type instead of string.
@click.argument("file")
@click.option("-r", "--report", is_flag=True)
def load(file, report):
    """Load PDF file."""
    if Path(file).exists():
        click.echo(f"Finding pages in { file }")
        readpdf = pypdf.PdfReader(file)
        totalpages = len(readpdf.pages)
        click.echo(f"{totalpages} pages in file")
        import_pages_input = click.prompt(
            "How many pages would you like to import? \n Press <Enter> for all pages.",
            default=totalpages,
        )
        df_ranking = pd.DataFrame()
        for i in range(import_pages_input):
            click.echo(f"Reading page {i + 1}")
            tables = read_pdf(
                file,
                flavor="stream",
                pages=str(i + 1),
                split_text=True,
                # not needed? table_areas=["50,810,435,50"],
                column_tol=1,
            )
            if report:
                click.echo(tables[0].parsing_report)

            df_ranking = pd.concat([df_ranking, tables[0].df], ignore_index=True)
        df_ranking = df_ranking.reset_index()
        df_ranking = df_ranking.drop(index=0)
        df_ranking.columns = ["player_id", "name", "country", "points", "position"]
        click.echo("Exporting to .csv")
        df_ranking.to_csv("ranking.csv", encoding="utf-8", index=False)
    else:
        click.echo(
            f"File '{file}' not found. For information on how to load a PDF file use 'fiprank load --help'"
        )


@cli.command()
def countries():
    """List countries found in ranking."""
    df_countrylist = pd.read_csv(csv_finder())
    click.echo(df_countrylist.country.unique())


@cli.command()
@click.argument("country")
def countryrank(country: str):
    """View ranked players from selected country"""
    click.echo(f"Players ranked from : {country}")
    ranking = pd.read_csv(csv_finder())
    click.echo(
        ranking[ranking.country == country]
        .drop("player_id", axis=1)
        .to_string(index=False)
    )


@cli.command()
def clean():
    """Fix various errors with encoding in the original PDF"""

    with open("ranking.csv", newline="", encoding="utf-8") as ranking_file, open(
        "ranking_clean.csv", "w", newline="", encoding="utf-8"
    ) as ranking_clean_file:
        reader = csv.reader(ranking_file)
        writer = csv.writer(ranking_clean_file)
        error_names = []
        for row in reader:
            if not row[1].isascii():
                try:
                    row[1] = (
                        row[1]
                        .encode("cp1252")
                        .decode(
                            "utf-8",
                        )
                    )
                except UnicodeEncodeError as e:
                    click.echo(f"ENCODE ERROR: {row[1], e}")
                    error_names.append(row[1])
                except UnicodeDecodeError as e:
                    # Hack to fix particular "xc2" error that only seems to affect capitalization
                    if "xc2" in str(e.object):
                        row[1] = row[1].encode("cp1252").decode(errors="ignore").title()
                    else:
                        error_names.append(row[1])
                        # Not clear if this can be used, leaving for now
                        # print(row[1].encode("raw_unicode_escape", ).decode())
                        # row[1] = row[1].encode("raw_unicode_escape", ).decode()
            writer.writerow(row)
    not_replaced = manual_replace(error_names)
    #todo input validation?
    show_diff = click.prompt("Show all changes made? (y/n)", default="n")
    if show_diff == "y":
        df1 = pd.read_csv("ranking.csv")
        df2 = pd.read_csv("ranking_clean.csv")
        print(df1.compare(df2, result_names=("PDF:", "New:")).to_string(index=False))
    if len(not_replaced) > 0:
        click.echo(f"Not able to clean: {not_replaced}")
    

    if ranking_clean.exists():
        ranking_original.unlink()
        

    
