from __future__ import division
from math import sqrt, erf, log
import StringIO
import collections


class Distribution(object):
    def __init__(self):
        self.n = 0
        self.sum = 0
        self.sum2 = 0
        self.max = float('-inf')
        self.min = float('+inf')

    def add_value(self, x):
        self.n += 1
        self.sum += x
        self.sum2 += x*x
        self.max = max(self.max, x)
        self.min = min(self.min, x)

    def mean(self):
        if self.n == 0:
            return 0
        return self.sum / self.n

    def sigma(self):
        if self.n < 2:
            return 0
        mean = self.mean()
        sigma2 = (self.sum2 - 2*mean*self.sum + mean*mean*self.n) / (self.n - 1)
        if sigma2 < 0:  # numerical errors
            sigma2 = 0
        return sqrt(sigma2)

    def to_html(self):
        if self.n == 0:
            return '--'
        if self.sigma() < 1e-10:
            return str(self.mean())
        return \
            '<span title="{}..{}">{:.3f} &plusmn; <i>{:.3f}</i></span>'.format(
                self.min, self.max, self.mean(), self.sigma())

    def prob_mean_larger(self, other):
        """
        Probability that actual mean of this dist is larger than of another.
        """
        if self.n == 0 or other.n == 0:
            return 0.5
        diff_mean = self.mean() - other.mean()

        sigma1 = self.sigma()
        sigma2 = other.sigma()
        # If we have no data about variance of one of the distributions,
        # we take it from another distribution.
        if other.n == 1:
            sigma2 = sigma1
        if self.n == 1:
            sigma1 = sigma2

        diff_sigma = sqrt(sigma1**2 + sigma2**2)

        if diff_sigma == 0:
            if diff_mean > 0:
                return 1
            elif diff_mean < 0:
                return 0
            else:
                return 0.5
        p = 0.5 * (1 + erf(diff_mean / (sqrt(2) * diff_sigma)))
        return p


def aggregate_stats(results):
    stats = collections.defaultdict(Distribution)
    for result in results:
        for dp in result['data_points']:
            for k, v in dp.items():
                if k != 'type':
                    stats[k].add_value(v)
        stats['log_score'].add_value(log(result['score']))
    return stats


def color_prob(p):
    if p < 0.5:
        red = 1 - 2 * p;
        return '#{:x}00'.format(int(15 * red))
    else:
        green = 2 * p - 1
        return '#0{:x}0'.format(int(15 * green))


def render_cell(results, baseline_results):
    fout = StringIO.StringIO()

    stats = aggregate_stats(results)
    baseline_stats = aggregate_stats(baseline_results)

    color = color_prob(stats['log_score'].prob_mean_larger(baseline_stats['log_score']))
    fout.write(
        '<span style="font-size:125%; font-weight:bold; color:{}">'
        'log_score = {}</span>'.format(
        color, stats['log_score'].to_html()))
    for k, v in sorted(stats.items()):
        if k != 'log_score':
            color = color_prob(v.prob_mean_larger(baseline_stats[k]))
            fout.write('<br>{} = <span style="color:{}">{}</span>'.format(
                k, color, v.to_html()))
    return fout.getvalue()


def render_table(results, baseline_results):
    fout = StringIO.StringIO()
    fout.write('<table>')
    fout.write('<tr> <th></th>')
    for colors in None, 4, 5, 6:
        fout.write('<th>colors = {}</th>'.format(colors or '*'))
    fout.write('</tr>')
    for n in [None] + list(range(8, 16 + 1)):
        fout.write('<tr>')
        fout.write('<th>n = {}</th>'.format(n or '*'))
        for colors in None, 4, 5, 6:
            filtered_results = []
            for result in results:
                if n and n != result['n']:
                    continue
                if colors and colors != result['colors']:
                    continue
                filtered_results.append(result)
            filtered_baseline_results = []
            for result in baseline_results:
                if n and n != result['n']:
                    continue
                if colors and colors != result['colors']:
                    continue
                filtered_baseline_results.append(result)

            if colors is None or n is None:
                fout.write('<td align="right" bgcolor=#eee>')
            else:
                fout.write('<td align="right">')
            fout.write(render_cell(filtered_results, filtered_baseline_results))
            fout.write('</td>')

        fout.write('</tr>')
    fout.write('</table>')
    return fout.getvalue()
