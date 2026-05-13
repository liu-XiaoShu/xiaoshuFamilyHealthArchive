"""当前异常细项判定（按自然年覆盖规则）。

规则概要：
- 先看**本年**（自然年）内该细项的所有记录，从新到旧找到第一条 abnormal 非空的记录；
  - ``False`` → 本年已复查且正常，覆盖往年异常；
  - ``True`` → 本年仍为异常。
- 若本年没有记录，或本年记录 abnormal 均为空：则从新到旧看**本年之前**的记录，
  找到第一条非空记录；若为 ``True`` 则仍视为当前异常（沿用），为 ``False`` 则不算异常。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from app.models import Observation


def _aware_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def calendar_year_bounds_utc(reference: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    ref = reference or datetime.now(timezone.utc)
    ref = _aware_utc(ref)
    y = ref.year
    start = datetime(y, 1, 1, tzinfo=timezone.utc)
    end = datetime(y + 1, 1, 1, tzinfo=timezone.utc)
    return start, end


def resolve_current_abnormal_for_indicator(
    observations: List[Observation],
    reference: Optional[datetime] = None,
) -> Tuple[bool, Optional[Observation], str]:
    """
    :param observations: 同一成员、同一 indicator_id 的全部 Observation（可不排序）
    :return: (是否当前异常, 作为判定依据的那条观测, 简要依据说明)
    """
    if not observations:
        return False, None, ""

    start, _end = calendar_year_bounds_utc(reference)

    cy_obs = [o for o in observations if start <= _aware_utc(o.measured_at) < _end]
    cy_desc = sorted(cy_obs, key=lambda o: (o.measured_at, o.id), reverse=True)

    def scan(chain: List[Observation]) -> Tuple[Optional[bool], Optional[Observation]]:
        for o in chain:
            if o.abnormal is False:
                return False, o
            if o.abnormal is True:
                return True, o
        return None, None

    if cy_desc:
        flag, wit = scan(cy_desc)
        if flag is False:
            return False, wit, "本年复查：正常"
        if flag is True:
            return True, wit, "本年记录：异常"

    pre_obs = [o for o in observations if _aware_utc(o.measured_at) < start]
    pre_desc = sorted(pre_obs, key=lambda o: (o.measured_at, o.id), reverse=True)
    flag2, wit2 = scan(pre_desc)
    if flag2 is False:
        return False, wit2, "最近记录：正常"
    if flag2 is True:
        return True, wit2, "本年尚无该项目复查，沿用最近异常记录"

    return False, None, ""
