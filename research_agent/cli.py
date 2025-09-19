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
@click.option("--include-samsic/--no-include-samsic", "include_samsic", default=True, show_default=True, help="Include local Samsic RFP docx")
@click.option("--doc", "docs", multiple=True, type=click.Path(path_type=pathlib.Path), help="Additional local documents to include")
@click.option("--local-max-chunks", "local_max_chunks", default=3, show_default=True, type=int, help="Max local document chunks to include")
@click.option("--bid", is_flag=True, help="Bid-writing mode: parse RFP and generate bid with explanations")
@click.option("--rfp-path", type=click.Path(path_type=pathlib.Path), help="Path to the RFP DOCX file")
def main(query: tuple[str, ...], max_results: int, model: str | None, out_path: pathlib.Path, include_samsic: bool, docs: tuple[pathlib.Path, ...], local_max_chunks: int, bid: bool, rfp_path: pathlib.Path | None) -> None:
	q = " ".join(query).strip()
	if not q and not bid:
		console.print("[red]Please provide a query[/red]")
		raise SystemExit(2)

	# Detect special phrase for bid mode
	if "write a bid for the RFP stored in file" in q.lower():
		bid = True
		if rfp_path is None:
			rfp_path = pathlib.Path("data/raw/RFP - Bid Management Systems - Samsic UK.docx")

	agent = ResearchAgent()

	if bid:
		if rfp_path is None or not rfp_path.exists():
			console.print(f"[red]RFP path not found: {rfp_path}[/red]")
			raise SystemExit(2)
		bid_md, rfp_items, evidence = agent.write_bid_for_rfp(rfp_path=rfp_path, max_results=max_results, local_max_chunks=local_max_chunks)
		out_path.write_text(bid_md, encoding="utf-8")
		console.print(f"\nParsed {len(rfp_items)} RFP items from {rfp_path}")
	else:
		local_docs: list[pathlib.Path] = list(docs)
		if include_samsic:
			samsic = pathlib.Path("data/raw/RFP - Bid Management Systems - Samsic UK.docx")
			if samsic.exists():
				local_docs.append(samsic)
		report, evidence = agent.run(q, max_results=max_results, local_docs=local_docs, local_max_chunks=local_max_chunks)
		out_path.write_text(report, encoding="utf-8")

	table = Table(title="Sources")
	table.add_column("#", justify="right")
	table.add_column("Title")
	table.add_column("URL")
	for e in evidence:
		table.add_row(str(e.index), e.title or "(no title)", e.url)
	console.print(table)
	console.print(f"\nSaved report to {out_path.resolve()}")


if __name__ == "__main__":
	main()
