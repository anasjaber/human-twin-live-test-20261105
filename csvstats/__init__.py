"""Streaming numeric summaries for CSV files."""

import argparse
import csv
import math
import sys
from dataclasses import dataclass, field
from typing import Iterable, TextIO


@dataclass
class ColumnStats:
    name: str
    count: int = 0
    minimum: float = math.inf
    maximum: float = -math.inf
    sum_partials: list[float] = field(default_factory=list)

    def add(self, value: float) -> None:
        self.count += 1
        self.minimum = min(self.minimum, value)
        self.maximum = max(self.maximum, value)
        # math.fsum needs an iterable, so retain non-overlapping roundoff
        # partials using its error-free addition algorithm rather than all cells.
        # Their size is bounded by float precision/exponent range, not row count.
        if self.sum_partials and math.isinf(self.sum_partials[-1]):
            return
        index = 0
        for partial in self.sum_partials:
            if abs(value) < abs(partial):
                value, partial = partial, value
            high = value + partial
            if math.isinf(high):
                # Once the running sum overflows, retain its sign. Counts and
                # bounds still include every subsequent finite numeric cell.
                self.sum_partials[:] = [high]
                return
            low = partial - (high - value)
            if low:
                self.sum_partials[index] = low
                index += 1
            value = high
        self.sum_partials[index:] = [value]

    @property
    def mean(self) -> float:
        try:
            total = math.fsum(self.sum_partials)
        except OverflowError:
            total = math.copysign(math.inf, self.sum_partials[-1])
        return total / self.count


def summarize(rows: Iterable[list[str]]) -> list[ColumnStats]:
    iterator = iter(rows)
    columns = [ColumnStats(name) for name in next(iterator, [])]
    for row in iterator:
        for column, cell in zip(columns, row):
            try:
                value = float(cell.strip())
            except ValueError:
                continue
            if math.isfinite(value):
                column.add(value)
    return [column for column in columns if column.count]


def _format_bound(value: float) -> str:
    return str(int(value)) if value.is_integer() else repr(value)


def main(
    argv: list[str],
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    parser = argparse.ArgumentParser(prog='csvstats')
    parser.add_argument('file', help='CSV file to summarize; use - for stdin')
    args = parser.parse_args(argv)
    stdin = sys.stdin if stdin is None else stdin
    stdout = sys.stdout if stdout is None else stdout
    stderr = sys.stderr if stderr is None else stderr
    try:
        if args.file == '-':
            columns = summarize(csv.reader(stdin))
        else:
            with open(args.file, encoding='utf-8-sig', newline='') as source:
                columns = summarize(csv.reader(source))
    except (OSError, UnicodeError, csv.Error) as error:
        reason = error.strerror if isinstance(error, OSError) and error.strerror else str(error)
        print(f'csvstats: error: {args.file}: {reason}', file=stderr)
        return 2
    for column in columns:
        print(f'{column.name} {column.count} {_format_bound(column.minimum)} '
              f'{_format_bound(column.maximum)} {column.mean:.2f}', file=stdout)
    return 0
