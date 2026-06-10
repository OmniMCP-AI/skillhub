"""Export JDY accounting reports for a target month.

This script uses a local Chrome profile via Browser Use to reuse the current
JDY login session, extracts cookies plus the app auth value, then calls the report
export APIs directly and downloads the generated XLSX files.
"""

from __future__ import annotations

import argparse
import asyncio
import tempfile
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

import requests

from browser_use import Browser


BASE_URL = 'https://vip1-hz.jdy.com'
ACCOUNTING_URL = (
	'https://vip1-hz.jdy.com/accounting/index.html'
	'?dbid=79559134792172&enterSource=&tab=&random=1780555263754'
)
DBID = '79559134792172'
STATE_PATH = Path(tempfile.gettempdir()) / 'jdy-auth.json'


@dataclass(frozen=True)
class ReportSpec:
	key: str
	label: str
	export_url: str
	async_job: bool

	def build_payload(self, period: str, session: requests.Session) -> dict[str, Any]:
		if self.key == 'balance':
			return {'type': '1', 'fromPeriod': period, 'toPeriod': period}
		if self.key == 'profit':
			return {'type': '1', 'fromPeriod': period, 'toPeriod': period}
		if self.key == 'item_profit':
			return build_item_profit_payload(session=session, period=period)
		if self.key == 'cash_flow_std':
			return {
				'periodType': '1',
				'periodParam': '1',
				'fromPeriod': period,
				'toPeriod': period,
			}
		if self.key == 'payable_tax':
			return {'type': '1', 'fromPeriod': period, 'toPeriod': period}
		if self.key == 'fee_detail':
			year = period[:4]
			payload = {
				'periodFrom': f'{year}-01',
				'periodTo': f'{period[:4]}-{period[4:]}',
				'accountNo': '',
				'accountType': '3',
				'showItem': False,
				'showYtdAmount': True,
				'showFullName': False,
				'classIds': None,
				'showProp': False,
				'showZero': False,
			}
			payload['periodFrom'] = payload['periodFrom'].replace('-', '')
			payload['periodTo'] = payload['periodTo'].replace('-', '')
			return payload
		raise ValueError(f'Unsupported report key: {self.key}')


@dataclass(frozen=True)
class ExportResult:
	spec: ReportSpec
	output_path: Path | None
	error: str | None


REPORTS: tuple[ReportSpec, ...] = (
	ReportSpec('balance', '资产负债表', f'{BASE_URL}/jdy-fi-rpt/{DBID}/v1/balance/export', True),
	ReportSpec('profit', '利润表', f'{BASE_URL}/jdy-fi-rpt/{DBID}/v1/profit/export', True),
	ReportSpec('item_profit', '项目利润表', f'{BASE_URL}/jdy-fi-rpt/{DBID}/v1/item/profit/export', True),
	ReportSpec('cash_flow_std', '标准现金流量表', f'{BASE_URL}/jdy-fi-rpt/{DBID}/v1/cash-flow/report/export', True),
	ReportSpec('payable_tax', '主要应交税金明细表', f'{BASE_URL}/jdy-fi-rpt/{DBID}/v1/payable-tax/export', True),
	ReportSpec('fee_detail', '费用明细表', f'{BASE_URL}/jdy-fi-rpt/{DBID}/v1/cost-detail/export', False),
)


def default_period() -> str:
	today = date.today()
	year = today.year
	month = today.month - 1
	if month == 0:
		year -= 1
		month = 12
	return f'{year:04d}{month:02d}'


async def get_auth_state(profile: str, headless: bool) -> tuple[str, dict[str, Any]]:
	browser = Browser.from_system_chrome(profile_directory=profile, headless=headless)
	await browser.start()
	try:
		page = await browser.get_current_page()
		await page.goto(ACCOUNTING_URL)
		await asyncio.sleep(6)
		app_auth_value = await page.evaluate("() => localStorage.getItem('accessToken') || ''")
		state = await browser.export_storage_state(STATE_PATH)
		return app_auth_value, state
	finally:
		await browser.kill()


def build_session(app_auth_value: str, state: dict[str, Any]) -> requests.Session:
	session = requests.Session()
	for cookie in state.get('cookies', []):
		session.cookies.set(
			cookie['name'],
			cookie['value'],
			domain=cookie.get('domain'),
			path=cookie.get('path'),
		)
	session.headers.update(
		{
			'app-token': app_auth_value,
			'ajax_flag': '1',
			'Content-Type': 'application/json;charset=UTF-8',
		}
	)
	return session


def wait_for_job_url(session: requests.Session, job_id: str, timeout_seconds: int) -> str:
	deadline = time.time() + timeout_seconds
	query_url = f'{BASE_URL}/jdy-fi-rpt/{DBID}/v1/common/job/result'
	while time.time() < deadline:
		response = session.post(query_url, json={'jobId': job_id}, timeout=30)
		response.raise_for_status()
		payload = response.json()
		data = payload.get('data') or {}
		status = data.get('jobStatus')
		if status == 3 and data.get('url'):
			return data['url']
		if status == 4:
			raise RuntimeError(f'Export job failed: {payload}')
		time.sleep(2)
	raise TimeoutError(f'Export job did not finish within {timeout_seconds} seconds: {job_id}')


def derive_filename(spec: ReportSpec, url: str, period: str) -> str:
	path_name = Path(unquote(urlparse(url).path)).name
	if path_name:
		return path_name
	return f'{period}_{spec.key}.xlsx'


def build_item_profit_payload(session: requests.Session, period: str) -> dict[str, Any]:
	params_url = f'{BASE_URL}/jdy-fi/{DBID}/rpt/v1/item/profit/params'
	params_response = session.get(params_url, timeout=30)
	params_response.raise_for_status()
	params_body = params_response.json()
	if params_body.get('errcode') not in (0, '0'):
		raise RuntimeError(f'项目利润表参数初始化失败: {params_body}')

	params_data = params_body.get('data') or {}
	item_class_raw = params_data.get('itemClassId')
	try:
		item_class_id = int(item_class_raw) if item_class_raw not in (None, '') else 6
	except (TypeError, ValueError):
		item_class_id = 6
	item_ids = [item['itemId'] for item in (params_data.get('items') or []) if item.get('itemId') is not None]
	period_types = [value for value in (params_data.get('periodTypes') or []) if value != '']

	check_url = f'{BASE_URL}/jdy-fi/{DBID}/rpt/v1/item/profit/isProfitAndLoss'
	check_response = session.post(check_url, json={'itemClassId': item_class_id}, timeout=30)
	check_response.raise_for_status()
	check_body = check_response.json()
	if check_body.get('errcode') not in (0, '0'):
		raise RuntimeError(f'项目利润表损益校验失败: {check_body}')
	if not check_body.get('data'):
		raise RuntimeError('项目利润表当前账套未配置可导出的辅助核算损益项目')
	if not item_ids:
		raise RuntimeError('项目利润表当前默认筛选没有任何辅助核算项目，需先在页面手动选择后再导出')
	if not period_types:
		raise RuntimeError('项目利润表当前默认筛选没有任何数据类型，需先在页面手动选择后再导出')

	return {
		'type': '1',
		'startYearPeriod': period,
		'endYearPeriod': period,
		'itemClassId': item_class_id,
	}


def prepare_fee_detail_export(session: requests.Session, payload: dict[str, Any]) -> None:
	query_url = f'{BASE_URL}/jdy-fi-rpt/{DBID}/v1/cost-detail/list'
	response = session.post(query_url, json=payload, timeout=30)
	response.raise_for_status()
	body = response.json()
	if body.get('errcode') not in (0, '0'):
		raise RuntimeError(f'费用明细表查询失败: {body}')


def export_report(
	session: requests.Session,
	spec: ReportSpec,
	period: str,
	output_dir: Path,
	timeout_seconds: int,
) -> Path:
	payload = spec.build_payload(period=period, session=session)
	if spec.key == 'fee_detail':
		prepare_fee_detail_export(session=session, payload=payload)
	response = session.post(spec.export_url, json=payload, timeout=30)
	response.raise_for_status()
	body = response.json()
	if body.get('errcode') not in (0, '0'):
		raise RuntimeError(f'{spec.label} export failed: {body}')

	if spec.async_job:
		job_id = body.get('data')
		if not job_id:
			raise RuntimeError(f'{spec.label} export did not return job id: {body}')
		download_url = wait_for_job_url(session, str(job_id), timeout_seconds=timeout_seconds)
	else:
		download_url = body.get('data')
		if isinstance(download_url, dict):
			download_url = download_url.get('url')
		if not download_url:
			raise RuntimeError(f'{spec.label} export did not return download URL: {body}')

	file_name = derive_filename(spec, download_url, period)
	output_path = output_dir / file_name
	download = session.get(download_url, timeout=60)
	download.raise_for_status()
	output_path.write_bytes(download.content)
	return output_path


def run_exports(
	session: requests.Session,
	period: str,
	output_dir: Path,
	timeout_seconds: int,
) -> list[ExportResult]:
	results: list[ExportResult] = []
	for spec in REPORTS:
		try:
			output_path = export_report(
				session=session,
				spec=spec,
				period=period,
				output_dir=output_dir,
				timeout_seconds=timeout_seconds,
			)
		except Exception as exc:
			results.append(ExportResult(spec=spec, output_path=None, error=str(exc)))
			continue
		results.append(ExportResult(spec=spec, output_path=output_path, error=None))
	return results


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description='Export JDY reports for a target month.')
	parser.add_argument(
		'--period',
		default=default_period(),
		help='Target period in YYYYMM format. Defaults to last month.',
	)
	parser.add_argument(
		'--profile',
		default='Profile 3',
		help='Chrome profile directory name from Browser.list_chrome_profiles()',
	)
	parser.add_argument('--headless', action='store_true', help='Run Browser Use without a visible browser window')
	parser.add_argument(
		'--output-dir',
		default='output/jdy-reports',
		help='Directory where exported XLSX files will be saved',
	)
	parser.add_argument(
		'--timeout-seconds',
		type=int,
		default=120,
		help='Maximum wait time for each async export job',
	)
	return parser.parse_args()


def main() -> int:
	args = parse_args()
	output_dir = Path(args.output_dir)
	output_dir.mkdir(parents=True, exist_ok=True)

	app_auth_value, state = asyncio.run(get_auth_state(profile=args.profile, headless=args.headless))
	if not app_auth_value:
		raise RuntimeError('Failed to read JDY accessToken from localStorage')

	session = build_session(app_auth_value=app_auth_value, state=state)
	results = run_exports(
		session=session,
		period=args.period,
		output_dir=output_dir,
		timeout_seconds=args.timeout_seconds,
	)
	failed = False
	for result in results:
		if result.error:
			failed = True
			print(f'{result.spec.label}\tERROR\t{result.error}')
		else:
			print(f'{result.spec.label}\tOK\t{result.output_path}')
	return 1 if failed else 0


if __name__ == '__main__':
	raise SystemExit(main())
