from __future__ import annotations

import pathlib
import datetime

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
@click.option("--versioned/--no-versioned", "versioned", default=False, show_default=True, help="Save bid with timestamp under reports/")
def main(query: tuple[str, ...], max_results: int, model: str | None, out_path: pathlib.Path, rfp_path: pathlib.Path | None, versioned: bool) -> None:
	q = " ".join(query).strip().lower()

	# Detect special phrase for default behavior
	if "write a bid for the rfp stored in file" in q:
		if rfp_path is None:
			rfp_path = pathlib.Path("data/raw/RFP - Bid Management Systems - Samsic UK.docx")

	if rfp_path is None or not rfp_path.exists():
		console.print("[red]Provide --rfp-path to the RFP DOCX or use: 'Write a bid for the RFP stored in file'[/red]")
		raise SystemExit(2)

	reports_dir = pathlib.Path("reports")
	if versioned:
		reports_dir.mkdir(parents=True, exist_ok=True)
		ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
		versioned_path = reports_dir / f"bid_{ts}.md"

	agent = ResearchAgent()
	bid_md, rfp_items, evidence = agent.write_bid_for_rfp(rfp_path=rfp_path, max_results=max_results)

	if versioned:
		versioned_path.write_text(bid_md, encoding="utf-8")
		latest_path = reports_dir / "bid_latest.md"
		latest_path.write_text(bid_md, encoding="utf-8")
		console.print(f"Saved versioned report to {versioned_path.resolve()} and updated {latest_path.name}")
	else:
		out_path.write_text(bid_md, encoding="utf-8")
		console.print(f"Saved report to {out_path.resolve()}")

	console.print(f"\nParsed {len(rfp_items)} RFP items from {rfp_path}")

	table = Table(title="Sources (Web)")
	table.add_column("#", justify="right")
	table.add_column("Title")
	table.add_column("URL")
	for e in evidence:
		table.add_row(str(e.index), e.title or "(no title)", e.url)
	console.print(table)


if __name__ == "__main__":
	main()
