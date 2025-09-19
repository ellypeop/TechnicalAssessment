from __future__ import annotations

import pathlib

import click
from rich.console import Console
from rich.table import Table

from .agent import ResearchAgent

console = Console()


@click.command()
@click.argument("query", nargs=-1)
@click.option("--max-results", "max_results", default=8, show_default=True, type=int)
@click.option("--model", default=None, help="Override LLM model")
@click.option("--out", "out_path", default="report.md", show_default=True, type=click.Path(path_type=pathlib.Path))
@click.option("--rfp-path", type=click.Path(path_type=pathlib.Path), help="Path to the RFP DOCX file")
def main(query: tuple[str, ...], max_results: int, model: str | None, out_path: pathlib.Path, rfp_path: pathlib.Path | None) -> None:
	q = " ".join(query).strip().lower()

	# Detect special phrase for default behavior
	if "write a bid for the rfp stored in file" in q:
		if rfp_path is None:
			rfp_path = pathlib.Path("data/raw/RFP - Bid Management Systems - Samsic UK.docx")

	if rfp_path is None or not rfp_path.exists():
		console.print("[red]Provide --rfp-path to the RFP DOCX or use: 'Write a bid for the RFP stored in file'[/red]")
		raise SystemExit(2)

	agent = ResearchAgent()
	bid_md, rfp_items, evidence = agent.write_bid_for_rfp(rfp_path=rfp_path, max_results=max_results)
	out_path.write_text(bid_md, encoding="utf-8")
	console.print(f"\nParsed {len(rfp_items)} RFP items from {rfp_path}")

	table = Table(title="Sources (Web)")
	table.add_column("#", justify="right")
	table.add_column("Title")
	table.add_column("URL")
	for e in evidence:
		table.add_row(str(e.index), e.title or "(no title)", e.url)
	console.print(table)
	console.print(f"\nSaved report to {out_path.resolve()}")


if __name__ == "__main__":
	main()
