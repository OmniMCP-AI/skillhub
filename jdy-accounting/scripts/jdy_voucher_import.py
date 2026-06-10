"""Import JDY vouchers from an Excel file using a local Chrome profile.

This script reuses a signed-in Chrome profile through Browser Use, opens the
voucher import flow in JDY accounting, uploads the given Excel file, chooses a
duplicate-voucher handling strategy, and confirms the import.
"""

from __future__ import annotations

import argparse
import asyncio
import re
from collections.abc import Sequence
from pathlib import Path

from browser_use import Browser
from browser_use.dom.views import EnhancedDOMTreeNode
from browser_use.skill_cli.actions import ActionHandler

DEFAULT_URL = 'https://vip1-hz.jdy.com/accounting/index.html?dbid=79559134792172&enterSource=&tab=&random=1780651539877'
DEFAULT_FILE = Path('20260605165228_凭证导入模板.xlsx')
SUCCESS_RE = re.compile(r'成功\d+条,\s*失败\d+条')


def normalize_text(value: str) -> str:
	"""Collapse whitespace so exact-text matching is stable across DOM variants."""
	return ' '.join(value.split())


def find_text_node(selector_map: dict[int, EnhancedDOMTreeNode], text: str) -> tuple[int, EnhancedDOMTreeNode]:
	"""Find the first interactive node whose meaningful text matches exactly."""
	target = normalize_text(text)
	for index, node in selector_map.items():
		candidates = [
			normalize_text(node.get_meaningful_text_for_llm()),
			normalize_text(node.get_all_children_text()),
			normalize_text(node.attributes.get('aria-label', '')),
			normalize_text(node.attributes.get('title', '')),
			normalize_text(node.attributes.get('placeholder', '')),
			normalize_text(node.attributes.get('value', '')),
		]
		if target in {candidate for candidate in candidates if candidate}:
			return index, node
	raise LookupError(f'未找到文本为“{text}”的可点击元素')


def find_file_input(selector_map: dict[int, EnhancedDOMTreeNode]) -> EnhancedDOMTreeNode:
	"""Find the visible file input from the interactive selector map."""
	for node in selector_map.values():
		if node.tag_name == 'input' and node.attributes.get('type', '').lower() == 'file':
			return node
	raise LookupError('未找到文件上传输入框')


def resolve_file_path(file_path: Path) -> Path:
	"""Resolve a voucher file from an explicit path or common download location."""
	candidates = [file_path.expanduser()]
	if not file_path.is_absolute():
		candidates.append(Path.cwd() / file_path)
		candidates.append(Path.home() / 'Downloads' / file_path)

	for candidate in candidates:
		resolved = candidate.resolve()
		if resolved.exists():
			return resolved
	return candidates[0].resolve()


async def click_text(actions: ActionHandler, text: str, pause_seconds: float) -> None:
	"""Refresh DOM state, click an exact-text element, and wait for UI to settle."""
	state = await actions.get_state()
	index, node = find_text_node(state.dom_state.selector_map, text)
	print(f'CLICK {text} {index}')
	await actions.click_element(node)
	await asyncio.sleep(pause_seconds)


async def upload_voucher_file(
	actions: ActionHandler,
	file_path: Path,
	duplicate_strategy: str,
	pause_seconds: float,
) -> str:
	"""Upload the Excel file, confirm the import, and return the final page text."""
	state = await actions.get_state()
	file_input = find_file_input(state.dom_state.selector_map)
	print(f'UPLOAD {file_input.backend_node_id} {file_path}')
	await actions.upload_file(file_input, str(file_path))
	await asyncio.sleep(pause_seconds)
	await click_text(actions, duplicate_strategy, pause_seconds)
	await click_text(actions, '确定', pause_seconds)
	await asyncio.sleep(pause_seconds * 3)
	page = await actions.bs.get_current_page()
	if page is None:
		raise RuntimeError('当前没有可用页面，无法读取导入结果')
	return await page.evaluate('() => document.body.innerText')


async def run_import(args: argparse.Namespace) -> str:
	"""Run the JDY voucher import flow in a Browser Use browser session."""
	file_path = resolve_file_path(args.file)
	if not file_path.exists():
		raise FileNotFoundError(f'文件不存在: {file_path}')
	if file_path.stat().st_size == 0:
		raise ValueError(f'文件为空: {file_path}')

	browser = Browser.from_system_chrome(
		profile_directory=args.profile,
		headless=args.headless,
		keep_alive=False,
		cross_origin_iframes=True,
		window_size={'width': 1440, 'height': 960},
		wait_between_actions=args.pause_seconds,
	)
	await browser.start()
	try:
		actions = ActionHandler(browser)
		await actions.navigate(args.url)
		await asyncio.sleep(args.initial_wait_seconds)
		await click_text(actions, '查凭证', args.pause_seconds)
		await click_text(actions, '导入', args.pause_seconds)
		body_text = await upload_voucher_file(
			actions=actions,
			file_path=file_path,
			duplicate_strategy=args.duplicate_strategy,
			pause_seconds=args.pause_seconds,
		)
		return body_text
	finally:
		await browser.kill()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(description='Import vouchers into JDY accounting from an Excel file.')
	parser.add_argument(
		'--url',
		default=DEFAULT_URL,
		help='JDY accounting page URL to open (default: %(default)s)',
	)
	parser.add_argument(
		'--file',
		type=Path,
		default=DEFAULT_FILE,
		help='Path to the voucher import Excel file (default: %(default)s)',
	)
	parser.add_argument(
		'--profile',
		default='Profile 3',
		help='Chrome profile directory name from Browser.list_chrome_profiles() (default: %(default)s)',
	)
	parser.add_argument('--headless', action='store_true', help='Run without a visible browser window')
	parser.add_argument(
		'--duplicate-strategy',
		default='重新编号',
		help='Exact visible text for the duplicate-voucher handling option (default: %(default)s)',
	)
	parser.add_argument(
		'--initial-wait-seconds',
		type=float,
		default=8.0,
		help='Seconds to wait after opening the JDY page before searching for controls',
	)
	parser.add_argument(
		'--pause-seconds',
		type=float,
		default=1.2,
		help='Seconds to wait after each interaction so modal UI can settle',
	)
	return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
	"""Run the import and print a concise result summary."""
	args = parse_args(argv)
	body_text = asyncio.run(run_import(args))
	match = SUCCESS_RE.search(body_text)
	if match:
		print(match.group(0))
	else:
		print(body_text)
	return 0


if __name__ == '__main__':
	raise SystemExit(main())
