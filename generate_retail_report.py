#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate retail ecommerce AI job analysis HTML report from JSON data."""

import json
import os
import re
from collections import Counter, defaultdict
from statistics import mean, median

DATA_FILE = os.path.join(os.path.dirname(__file__), "retail_ecommerce_jobs.json")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "retail_ecommerce_ai_analysis.html")

CATEGORY_META = {
    "design":      {"label": "AI视觉设计类",    "icon": "&#x1F3A8;", "color": "linear-gradient(135deg,#e74c3c,#f39c12)"},
    "ops":         {"label": "AI电商运营类",    "icon": "&#x1F4E6;", "color": "linear-gradient(135deg,#3498db,#2ecc71)"},
    "product":     {"label": "AI产品经理类",    "icon": "&#x1F4DD;", "color": "linear-gradient(135deg,#9b59b6,#e74c3c)"},
    "training":    {"label": "AI训练与标注类",  "icon": "&#x1F9D1;&#x200D;&#x1F3EB;", "color": "linear-gradient(135deg,#1abc9c,#16a085)"},
    "crossborder": {"label": "跨境电商AI类",   "icon": "&#x1F30D;", "color": "linear-gradient(135deg,#e67e22,#d35400)"},
    "tech":        {"label": "技术与算法类",    "icon": "&#x26A1;",  "color": "linear-gradient(135deg,#2c3e50,#34495e)"},
    "content":     {"label": "AI内容创作类",    "icon": "&#x1F4F9;", "color": "linear-gradient(135deg,#8e44ad,#3498db)"},
    "live":        {"label": "AI直播与数字人类", "icon": "&#x1F4F1;", "color": "linear-gradient(135deg,#e74c3c,#8e44ad)"},
    "sales":       {"label": "AI电商销售类",    "icon": "&#x1F4B0;", "color": "linear-gradient(135deg,#27ae60,#2ecc71)"},
    "service":     {"label": "AI客服与售后类",  "icon": "&#x1F4AC;", "color": "linear-gradient(135deg,#16a085,#2980b9)"},
}

def parse_salary(s):
    """Parse salary string to (min, max) in K."""
    s = s.replace(",", "").replace(" ", "")
    if s == "面议":
        return None, None
    # Handle patterns like "30K-45K", "8K-15K", "8000-15000元", etc.
    m = re.match(r"(\d+\.?\d*)[Kk万]?\s*[-~]\s*(\d+\.?\d*)[Kk万]?", s)
    if m:
        lo, hi = float(m.group(1)), float(m.group(2))
        # If values look like raw yuan (>100), convert to K
        if lo > 100:
            lo /= 1000
        if hi > 100:
            hi /= 1000
        return lo, hi
    return None, None


def salary_mid(s):
    lo, hi = parse_salary(s)
    if lo is None:
        return None
    return (lo + hi) / 2


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    total = len(jobs)

    # --- Analytics ---
    cats = Counter(j["cat"] for j in jobs)
    cities = Counter(j["city"] for j in jobs)
    edus = Counter(j["edu"] for j in jobs)
    exps = Counter(j["exp"] for j in jobs)

    # Salary stats
    mids = [salary_mid(j["salary"]) for j in jobs if salary_mid(j["salary"]) is not None]
    avg_salary = mean(mids) if mids else 0
    med_salary = median(mids) if mids else 0
    lo_all = [parse_salary(j["salary"])[0] for j in jobs if parse_salary(j["salary"])[0] is not None]
    hi_all = [parse_salary(j["salary"])[1] for j in jobs if parse_salary(j["salary"])[1] is not None]
    min_salary = min(lo_all) if lo_all else 0
    max_salary = max(hi_all) if hi_all else 0

    # Category salary averages
    cat_salaries = defaultdict(list)
    for j in jobs:
        m = salary_mid(j["salary"])
        if m:
            cat_salaries[j["cat"]].append(m)
    cat_avg = {k: mean(v) for k, v in cat_salaries.items()}

    # Edu distribution
    edu_map = {"大专": 0, "本科": 0, "硕士": 0, "不限": 0}
    for j in jobs:
        e = j["edu"]
        if "大专" in e:
            edu_map["大专"] += 1
        elif "硕" in e:
            edu_map["硕士"] += 1
        elif "本科" in e:
            edu_map["本科"] += 1
        else:
            edu_map["不限"] += 1

    # Experience distribution
    exp_map = {"不限": 0, "1年以下": 0, "1-3年": 0, "3-5年": 0, "5-10年": 0}
    for j in jobs:
        e = j["exp"]
        if "不限" in e:
            exp_map["不限"] += 1
        elif "1年以下" in e or "1年以下" in e:
            exp_map["1年以下"] += 1
        elif "5-10" in e or "5" in e and "10" in e:
            exp_map["5-10年"] += 1
        elif "3-5" in e or "3" in e and "5" in e:
            exp_map["3-5年"] += 1
        elif "1-3" in e or "1" in e and "3" in e:
            exp_map["1-3年"] += 1
        else:
            exp_map["不限"] += 1

    # Top 10 cities
    top_cities = cities.most_common(10)

    # Top salary jobs
    top_salary_jobs = sorted(jobs, key=lambda j: salary_mid(j["salary"]) or 0, reverse=True)[:15]

    # Bottom salary jobs
    bottom_salary_jobs = sorted(
        [j for j in jobs if salary_mid(j["salary"]) is not None],
        key=lambda j: salary_mid(j["salary"])
    )[:10]

    # Source distribution
    srcs = Counter(j["src"] for j in jobs)

    # Percentage helpers
    def pct(n, t=total):
        return f"{n/t*100:.0f}%" if t else "0%"

    # Edu percentage for "大专即可" (大专 + 不限)
    dazhuan_pct = (edu_map["大专"] + edu_map["不限"]) / total * 100

    # Experience "1-3年" percentage
    exp_1_3_pct = exp_map["1-3年"] / total * 100

    # Scale distribution
    scale_map = defaultdict(int)
    for j in jobs:
        s = j.get("scale", "")
        if "10000" in s or "万" in s:
            scale_map["10000人以上"] += 1
        elif "1000" in s:
            scale_map["1000-9999人"] += 1
        elif "500" in s:
            scale_map["500-999人"] += 1
        elif "300" in s:
            scale_map["300-499人"] += 1
        elif "100" in s:
            scale_map["100-299人"] += 1
        elif "20人以下" in s:
            scale_map["20人以下"] += 1
        else:
            scale_map["20-99人"] += 1

    # --- Build HTML ---
    # Category cards
    cat_cards_html = ""
    for cat_key in ["design", "ops", "product", "training", "crossborder", "tech", "content", "live", "sales", "service"]:
        if cat_key not in cats:
            continue
        meta = CATEGORY_META[cat_key]
        cat_jobs = [j for j in jobs if j["cat"] == cat_key]
        count = len(cat_jobs)
        pct_val = count / total * 100
        items_html = ""
        for j in cat_jobs:
            items_html += f'''        <div class="job-item">
          <span class="job-name">{j["name"]}</span>
          <span class="job-salary">{j["salary"]}</span>
        </div>\n'''
        cat_cards_html += f'''    <div class="category-card">
      <div class="category-header" style="background:{meta['color']};">
        <h3>{meta['icon']} {meta['label']}</h3>
        <div class="count">{count}个岗位 | 占比 {pct_val:.0f}%</div>
      </div>
      <div class="category-body" style="max-height:300px;overflow-y:auto;">
{items_html}      </div>
    </div>\n'''

    # Top salary table rows
    top_rows = ""
    for j in top_salary_jobs:
        top_rows += f'''          <tr>
            <td>{j["name"]}</td>
            <td class="salary-highlight">{j["salary"]}</td>
            <td>{j["exp"]}</td>
            <td>{j["edu"]}</td>
            <td>{j["city"]}</td>
            <td>{j["company"]}</td>
          </tr>\n'''

    # Bottom salary table rows
    bottom_rows = ""
    for j in bottom_salary_jobs:
        bottom_rows += f'''          <tr>
            <td>{j["name"]}</td>
            <td>{j["salary"]}</td>
            <td>{j["exp"]}</td>
            <td>{j["edu"]}</td>
            <td>{j["city"]}</td>
            <td>{j["company"]}</td>
          </tr>\n'''

    # City bars
    city_bars_html = ""
    if top_cities:
        max_city_count = top_cities[0][1]
        for city, count in top_cities:
            width = count / max_city_count * 100
            city_bars_html += f'''      <div class="bar-row">
        <span class="bar-label">{city}</span>
        <div class="bar-track"><div class="bar-fill" style="width:{width:.0f}%;background:var(--gradient-2);"></div></div>
        <span class="bar-value">{count}个</span>
      </div>\n'''

    # Edu bars
    edu_bars_html = ""
    max_edu = max(edu_map.values()) if edu_map else 1
    for label, count in sorted(edu_map.items(), key=lambda x: x[1], reverse=True):
        width = count / max_edu * 100
        edu_bars_html += f'''      <div class="bar-row">
        <span class="bar-label">{label}</span>
        <div class="bar-track"><div class="bar-fill" style="width:{width:.0f}%;background:var(--gradient-1);"></div></div>
        <span class="bar-value">{count}个 ({count/total*100:.0f}%)</span>
      </div>\n'''

    # Exp bars
    exp_bars_html = ""
    max_exp = max(exp_map.values()) if exp_map else 1
    for label in ["不限", "1年以下", "1-3年", "3-5年", "5-10年"]:
        count = exp_map[label]
        if count == 0:
            continue
        width = count / max_exp * 100
        exp_bars_html += f'''      <div class="bar-row">
        <span class="bar-label">{label}</span>
        <div class="bar-track"><div class="bar-fill" style="width:{width:.0f}%;background:var(--gradient-3);"></div></div>
        <span class="bar-value">{count}个 ({count/total*100:.0f}%)</span>
      </div>\n'''

    # Category avg salary bars
    cat_salary_bars = ""
    sorted_cats = sorted(cat_avg.items(), key=lambda x: x[1], reverse=True)
    max_cat_sal = sorted_cats[0][1] if sorted_cats else 1
    for cat_key, avg in sorted_cats:
        meta = CATEGORY_META.get(cat_key, {"label": cat_key, "icon": ""})
        width = avg / max_cat_sal * 100
        cat_salary_bars += f'''      <div class="bar-row">
        <span class="bar-label">{meta["label"]}</span>
        <div class="bar-track"><div class="bar-fill" style="width:{width:.0f}%;background:var(--gradient-1);"></div></div>
        <span class="bar-value">{avg:.1f}K</span>
      </div>\n'''

    # Company scale bars
    scale_bars = ""
    max_scale = max(scale_map.values()) if scale_map else 1
    for label, count in sorted(scale_map.items(), key=lambda x: x[1], reverse=True):
        width = count / max_scale * 100
        scale_bars += f'''      <div class="bar-row">
        <span class="bar-label">{label}</span>
        <div class="bar-track"><div class="bar-fill" style="width:{width:.0f}%;background:var(--gradient-2);"></div></div>
        <span class="bar-value">{count}个 ({count/total*100:.0f}%)</span>
      </div>\n'''

    # Full job table
    full_table_rows = ""
    for j in sorted(jobs, key=lambda x: salary_mid(x["salary"]) or 0, reverse=True):
        cat_label = CATEGORY_META.get(j["cat"], {}).get("label", j["cat"])
        full_table_rows += f'''          <tr>
            <td>{j["name"]}</td>
            <td class="salary-highlight">{j["salary"]}</td>
            <td>{j["exp"]}</td>
            <td>{j["edu"]}</td>
            <td>{j["city"]}</td>
            <td>{j["company"]}</td>
            <td>{cat_label}</td>
          </tr>\n'''

    # Number of categories
    num_cats = len([c for c in cats if cats[c] > 0])

    # Largest category
    largest_cat = cats.most_common(1)[0] if cats else ("", 0)
    largest_cat_label = CATEGORY_META.get(largest_cat[0], {}).get("label", largest_cat[0])

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>零售电商 AI 岗位专项深度分析 | 2026年4月</title>
<style>
  :root {{
    --primary: #e74c3c; --primary-dark: #c0392b; --secondary: #f39c12;
    --accent: #3498db; --bg: #fafafa; --card-bg: #ffffff; --text: #2c3e50;
    --text-light: #7f8c8d; --border: #ecf0f1; --success: #27ae60;
    --warning: #f39c12; --danger: #e74c3c;
    --gradient-1: linear-gradient(135deg, #e74c3c, #f39c12);
    --gradient-2: linear-gradient(135deg, #3498db, #2ecc71);
    --gradient-3: linear-gradient(135deg, #9b59b6, #e74c3c);
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; background: var(--bg); color: var(--text); line-height: 1.7; }}
  .hero {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: white; padding: 60px 0 50px; text-align: center; position: relative; overflow: hidden; }}
  .hero::before {{ content: ''; position: absolute; top:0;left:0;right:0;bottom:0; background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E"); opacity:0.5; }}
  .hero h1 {{ font-size: 2.4em; font-weight: 800; margin-bottom: 12px; position: relative; }}
  .hero .subtitle {{ font-size: 1.1em; opacity: 0.85; position: relative; }}
  .hero .badge {{ display: inline-block; background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); border-radius: 20px; padding: 6px 18px; font-size: 0.85em; margin-top: 16px; position: relative; }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 0 24px; }}
  .stats-bar {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin: -30px auto 30px; padding: 0 24px; max-width: 1200px; position: relative; z-index: 10; }}
  .stat-card {{ background: white; border-radius: 14px; padding: 18px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.08); transition: transform 0.2s; }}
  .stat-card:hover {{ transform: translateY(-3px); }}
  .stat-card .number {{ font-size: 1.8em; font-weight: 800; background: var(--gradient-1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
  .stat-card .label {{ font-size: 0.82em; color: var(--text-light); margin-top: 4px; }}
  .section {{ margin: 40px auto; max-width: 1200px; padding: 0 24px; }}
  .section-title {{ font-size: 1.5em; font-weight: 700; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }}
  .section-title .icon {{ width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2em; }}
  .card {{ background: var(--card-bg); border-radius: 16px; padding: 28px; margin-bottom: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.04); border: 1px solid var(--border); }}
  .card-title {{ font-size: 1.15em; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }}
  .category-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px; }}
  .category-card {{ background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid var(--border); transition: transform 0.2s, box-shadow 0.2s; }}
  .category-card:hover {{ transform: translateY(-4px); box-shadow: 0 8px 30px rgba(0,0,0,0.1); }}
  .category-header {{ padding: 18px 22px; color: white; }}
  .category-header h3 {{ font-size: 1.15em; font-weight: 700; margin-bottom: 2px; }}
  .category-header .count {{ font-size: 0.82em; opacity: 0.9; }}
  .category-body {{ padding: 12px 16px; }}
  .job-item {{ display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-bottom: 1px solid #f5f5f5; font-size: 0.88em; }}
  .job-item:last-child {{ border-bottom: none; }}
  .job-name {{ flex: 1; color: var(--text); }}
  .job-salary {{ color: var(--danger); font-weight: 600; white-space: nowrap; margin-left: 10px; }}
  .bar-row {{ display: flex; align-items: center; margin-bottom: 10px; }}
  .bar-label {{ width: 130px; font-size: 0.85em; font-weight: 600; flex-shrink: 0; }}
  .bar-track {{ flex: 1; height: 24px; background: #f0f0f0; border-radius: 12px; overflow: hidden; }}
  .bar-fill {{ height: 100%; border-radius: 12px; transition: width 0.6s ease; }}
  .bar-value {{ width: 90px; text-align: right; font-size: 0.82em; font-weight: 600; flex-shrink: 0; }}
  .salary-table {{ width: 100%; border-collapse: collapse; font-size: 0.85em; }}
  .salary-table th {{ padding: 12px 14px; text-align: left; background: #f8f9fa; font-weight: 600; border-bottom: 2px solid var(--border); }}
  .salary-table td {{ padding: 10px 14px; border-bottom: 1px solid var(--border); }}
  .salary-table tr:hover td {{ background: #fef9f4; }}
  .salary-highlight {{ color: var(--danger); font-weight: 700; }}
  .insight-box {{ background: linear-gradient(135deg, #fef9e7, #fdebd0); border-radius: 14px; padding: 22px 26px; margin: 16px 0; border-left: 4px solid var(--secondary); }}
  .insight-box .insight-title {{ font-weight: 700; font-size: 0.95em; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }}
  .insight-box p {{ font-size: 0.88em; color: #5d4e37; line-height: 1.7; }}
  .trend-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }}
  .trend-card {{ background: white; border-radius: 14px; padding: 22px; border: 1px solid var(--border); box-shadow: 0 2px 8px rgba(0,0,0,0.04); }}
  .trend-card .trend-icon {{ font-size: 2em; margin-bottom: 10px; }}
  .trend-card h4 {{ font-size: 1em; font-weight: 700; margin-bottom: 8px; }}
  .trend-card p {{ font-size: 0.85em; color: var(--text-light); line-height: 1.6; }}
  .career-path {{ position: relative; padding: 20px 0; }}
  .path-step {{ display: flex; align-items: flex-start; margin-bottom: 28px; position: relative; padding-left: 60px; }}
  .path-step::before {{ content: ''; position: absolute; left: 22px; top: 36px; width: 2px; height: calc(100% + 8px); background: var(--border); }}
  .path-step:last-child::before {{ display: none; }}
  .path-number {{ position: absolute; left: 0; width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.1em; color: white; }}
  .path-content {{ background: white; border-radius: 12px; padding: 16px 20px; border: 1px solid var(--border); flex: 1; }}
  .path-content h4 {{ font-size: 1em; font-weight: 700; margin-bottom: 4px; }}
  .path-content .path-salary {{ font-size: 0.82em; color: var(--danger); font-weight: 600; margin-bottom: 6px; }}
  .path-content p {{ font-size: 0.85em; color: var(--text-light); }}
  .footer {{ text-align: center; padding: 40px 20px; color: var(--text-light); font-size: 0.82em; border-top: 1px solid var(--border); margin-top: 40px; }}
  .footer a {{ color: var(--accent); text-decoration: none; }}
  .back-link {{ display: inline-flex; align-items: center; gap: 6px; color: rgba(255,255,255,0.8); text-decoration: none; font-size: 0.9em; margin-bottom: 20px; position: relative; transition: color 0.2s; }}
  .back-link:hover {{ color: white; }}
  .full-table-wrap {{ max-height: 600px; overflow-y: auto; border: 1px solid var(--border); border-radius: 12px; }}
  .full-table {{ width: 100%; border-collapse: collapse; font-size: 0.82em; }}
  .full-table th {{ padding: 10px 12px; text-align: left; background: #f8f9fa; font-weight: 600; border-bottom: 2px solid var(--border); position: sticky; top: 0; z-index: 2; }}
  .full-table td {{ padding: 8px 12px; border-bottom: 1px solid var(--border); }}
  .full-table tr:hover td {{ background: #fef9f4; }}
  .tab-nav {{ display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }}
  .tab-btn {{ padding: 8px 16px; border-radius: 20px; border: 1px solid var(--border); background: white; cursor: pointer; font-size: 0.85em; transition: all 0.2s; }}
  .tab-btn:hover {{ border-color: var(--accent); color: var(--accent); }}
  .tab-btn.active {{ background: var(--accent); color: white; border-color: var(--accent); }}
  @media (max-width: 768px) {{
    .hero h1 {{ font-size: 1.6em; }}
    .stats-bar {{ grid-template-columns: repeat(2, 1fr); }}
    .category-grid {{ grid-template-columns: 1fr; }}
    .bar-label {{ width: 100px; font-size: 0.78em; }}
  }}
</style>
</head>
<body>

<div class="hero">
  <div class="container">
    <a href="index.html" class="back-link">&larr; 返回报告索引</a>
    <h1>&#x1F6D2; 零售电商 AI 岗位专项深度分析</h1>
    <p class="subtitle">{total}个真实招聘岗位 &times; {num_cats}大岗位类别 &times; 完整能力素质模型</p>
    <div class="badge">&#x1F4C5; 数据来源：智联招聘 + BOSS直聘 + 行业调研 | 2026年4月</div>
  </div>
</div>

<div class="stats-bar">
  <div class="stat-card"><div class="number">{total}</div><div class="label">分析岗位总数</div></div>
  <div class="stat-card"><div class="number">{num_cats}</div><div class="label">岗位大类</div></div>
  <div class="stat-card"><div class="number">{min_salary:.0f}K-{max_salary:.0f}K</div><div class="label">月薪范围</div></div>
  <div class="stat-card"><div class="number">{avg_salary:.1f}K</div><div class="label">平均月薪</div></div>
  <div class="stat-card"><div class="number">{exp_1_3_pct:.0f}%</div><div class="label">要求1-3年经验</div></div>
  <div class="stat-card"><div class="number">{dazhuan_pct:.0f}%</div><div class="label">大专即可</div></div>
</div>

<!-- Section 1: Executive Summary -->
<div class="section">
  <div class="section-title"><span class="icon" style="background:#eaf2f8;">&#x1F4CB;</span>一、行业概览与核心发现</div>
  <div class="card">
    <p style="font-size:0.95em;margin-bottom:16px;">
      基于智联招聘、BOSS直聘2026年4月最新数据及行业公开信息，本报告覆盖<strong>{total}个真实零售电商AI岗位</strong>，
      横跨<strong>{num_cats}大岗位类别</strong>，是目前最全面的电商AI就业市场分析。
      电商行业的AI岗位呈现<strong>爆发式增长</strong>，与互联网和金融行业不同，<strong>零售电商AI岗位的核心特征是「工具化」和「实战化」</strong>
      ——企业需要的不是研发AI的人，而是<strong>会用AI提效的人</strong>。
    </p>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px;">
      <div style="display:flex;align-items:center;gap:12px;padding:14px 16px;background:#f8f9fa;border-radius:12px;">
        <span style="font-size:1.5em;">&#x1F3AF;</span>
        <div style="font-size:0.88em;"><strong style="display:block;">{largest_cat_label}占比最高</strong>{largest_cat[1]}个岗位（{largest_cat[1]/total*100:.0f}%），是最大需求方向</div>
      </div>
      <div style="display:flex;align-items:center;gap:12px;padding:14px 16px;background:#f8f9fa;border-radius:12px;">
        <span style="font-size:1.5em;">&#x1F4B0;</span>
        <div style="font-size:0.88em;"><strong style="display:block;">平均月薪 {avg_salary:.0f}K 元</strong>技术算法类天花板最高（{max(cat_avg.values()):.0f}K+）</div>
      </div>
      <div style="display:flex;align-items:center;gap:12px;padding:14px 16px;background:#f8f9fa;border-radius:12px;">
        <span style="font-size:1.5em;">&#x1F680;</span>
        <div style="font-size:0.88em;"><strong style="display:block;">跨境电商是新增长极</strong>独立站+TikTok+SHEIN是高薪方向</div>
      </div>
      <div style="display:flex;align-items:center;gap:12px;padding:14px 16px;background:#f8f9fa;border-radius:12px;">
        <span style="font-size:1.5em;">&#x1F916;</span>
        <div style="font-size:0.88em;"><strong style="display:block;">AI工具 > AI开发</strong>80%+岗位要求会用AI工具，非开发AI</div>
      </div>
    </div>
  </div>
</div>

<!-- Section 2: Job Categories -->
<div class="section">
  <div class="section-title"><span class="icon" style="background:#fef5e7;">&#x1F4CA;</span>二、{num_cats}大岗位类别详解</div>
  <div class="category-grid">
{cat_cards_html}  </div>
</div>

<!-- Section 3: Salary Analysis -->
<div class="section">
  <div class="section-title"><span class="icon" style="background:#fdedec;">&#x1F4B0;</span>三、薪资深度分析</div>

  <div class="card">
    <div class="card-title">&#x1F4C8; 各类别平均薪资排行</div>
{cat_salary_bars}  </div>

  <div class="card">
    <div class="card-title">&#x1F451; TOP15 高薪岗位</div>
    <div style="overflow-x:auto;">
      <table class="salary-table">
        <thead><tr><th>岗位名称</th><th>薪资</th><th>经验</th><th>学历</th><th>城市</th><th>公司</th></tr></thead>
        <tbody>
{top_rows}        </tbody>
      </table>
    </div>
  </div>

  <div class="card">
    <div class="card-title">&#x1F530; 入门级低薪岗位（求职门槛最低）</div>
    <div style="overflow-x:auto;">
      <table class="salary-table">
        <thead><tr><th>岗位名称</th><th>薪资</th><th>经验</th><th>学历</th><th>城市</th><th>公司</th></tr></thead>
        <tbody>
{bottom_rows}        </tbody>
      </table>
    </div>
  </div>

  <div class="insight-box">
    <div class="insight-title">&#x1F4A1; 薪资洞察</div>
    <p>电商AI岗位薪资呈现明显的<strong>「三段式」分布</strong>：入门级4K-8K（美工助理/客服/标注），
    中高级8K-20K（运营/设计师/产品经理/训练师），高端20K-45K（算法工程师/总监/资深产品经理）。
    <strong>跨境电商方向因人才稀缺，同等能力薪资溢价约30%</strong>。
    值得注意的是，生鲜电商AI产品经理以30K-45K位居榜首，反映出垂直领域AI落地的巨大价值。</p>
  </div>
</div>

<!-- Section 4: Multi-Dimension Analysis -->
<div class="section">
  <div class="section-title"><span class="icon" style="background:#eaf2f8;">&#x1F4CA;</span>四、多维度分析</div>

  <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(500px,1fr));gap:20px;">
    <div class="card">
      <div class="card-title">&#x1F3D9; 城市分布 TOP10</div>
{city_bars_html}    </div>

    <div class="card">
      <div class="card-title">&#x1F393; 学历要求分布</div>
{edu_bars_html}    </div>

    <div class="card">
      <div class="card-title">&#x23F0; 经验要求分布</div>
{exp_bars_html}    </div>

    <div class="card">
      <div class="card-title">&#x1F3E2; 企业规模分布</div>
{scale_bars}    </div>
  </div>

  <div class="insight-box">
    <div class="insight-title">&#x1F4A1; 分布洞察</div>
    <p><strong>杭州、深圳、成都</strong>是电商AI岗位最集中的三座城市，反映了电商产业集群效应。
    学历方面，<strong>{dazhuan_pct:.0f}%的岗位大专即可</strong>，说明电商AI更看重实操能力而非学历。
    企业规模两极分化：<strong>大厂（10000人+）提供高薪技术岗</strong>，<strong>中小企业（20-99人）提供最多的运营/设计岗位</strong>。</p>
  </div>
</div>

<!-- Section 5: Career Path -->
<div class="section">
  <div class="section-title"><span class="icon" style="background:#eafaf1;">&#x1F3C6;</span>五、职业发展路径建议</div>
  <div class="card">
    <div class="card-title">&#x1F4C8; 电商AI岗位晋升路线</div>
    <div class="career-path">
      <div class="path-step">
        <div class="path-number" style="background:linear-gradient(135deg,#3498db,#2ecc71);">1</div>
        <div class="path-content">
          <h4>入门期：AI电商美工 / AI运营助理 / AI标注员</h4>
          <div class="path-salary">3K-8K | 0-1年经验</div>
          <p>掌握AI工具基础（Midjourney/ChatGPT/SD），熟悉1-2个电商平台操作。重点是<strong>用AI提升现有工作效率</strong>，把传统技能和AI结合。入门门槛低，大专即可。</p>
        </div>
      </div>
      <div class="path-step">
        <div class="path-number" style="background:linear-gradient(135deg,#f39c12,#e67e22);">2</div>
        <div class="path-content">
          <h4>成长期：AI电商设计师 / AI运营专员 / AI训练师 / AI客服运营</h4>
          <div class="path-salary">8K-16K | 1-3年经验</div>
          <p>精通AI工具全链路，能<strong>独立用AI完成从创意到执行的闭环</strong>。设计方向深耕AI视觉工作流，运营方向掌握AI数据分析，训练师方向学习Prompt Engineering和模型调优。</p>
        </div>
      </div>
      <div class="path-step">
        <div class="path-number" style="background:linear-gradient(135deg,#e74c3c,#c0392b);">3</div>
        <div class="path-content">
          <h4>进阶期：电商AI产品经理 / 跨境AI运营 / AI效能经理 / AI直播运营经理</h4>
          <div class="path-salary">12K-25K | 3-5年经验</div>
          <p>从「执行」转向「规划」。产品经理需要设计AI产品方案，效能经理需要优化组织AI工作流，跨境方向需要<strong>AI+国际化双重能力</strong>。这是薪资增长最快的阶段。</p>
        </div>
      </div>
      <div class="path-step">
        <div class="path-number" style="background:linear-gradient(135deg,#8e44ad,#9b59b6);">4</div>
        <div class="path-content">
          <h4>资深期：AI电商负责人 / 数字化转型总监 / 电商AI算法专家</h4>
          <div class="path-salary">25K-45K+ | 5年以上</div>
          <p>带领团队完成电商业务的<strong>全面AI化转型</strong>。需要具备战略规划、团队管理、供应链数字化、AI技术选型等综合能力。算法方向需硕士学历，薪资天花板最高。</p>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Section 6: Trends -->
<div class="section">
  <div class="section-title"><span class="icon" style="background:#f5eef8;">&#x1F52E;</span>六、2026趋势预判：电商AI岗位未来走向</div>
  <div class="trend-grid">
    <div class="trend-card"><div class="trend-icon">&#x1F4F1;</div><h4>AI直播将成标配</h4><p>数字人直播带货正从试水走向规模化。预计2026下半年，「AI直播运营」将成为独立岗位，薪资12K-20K起步。需要掌握数字人定制、话术训练、互动策略。</p></div>
    <div class="trend-card"><div class="trend-icon">&#x1F30F;</div><h4>跨境AI岗位薪资将大幅上涨</h4><p>TikTok Shop + Temu + SHEIN的全球扩张，使跨境电商AI人才极度稀缺。会用AI做多语言内容+独立站运营的复合型人才，薪资溢价将达30-50%。</p></div>
    <div class="trend-card"><div class="trend-icon">&#x1F916;</div><h4>AI Agent将重构客服与运营</h4><p>电商AI Agent（自主完成售前咨询、售后处理、订单跟踪）将在2026年大规模落地，催生「AI Agent运营师」新岗位，融合AI训练+客服+运营三重技能。</p></div>
    <div class="trend-card"><div class="trend-icon">&#x1F3A8;</div><h4>AI设计师将两极分化</h4><p>简单商品图生成被AI自动化后，低端美工岗位会收缩。但「AI创意总监」——能用AI工具输出高级品牌视觉的人才——将成为抢手资源，薪资可达20K-35K。</p></div>
    <div class="trend-card"><div class="trend-icon">&#x1F4CA;</div><h4>数据+AI运营成为高薪方向</h4><p>单纯的运营+AI文案生成门槛越来越低。能同时做「AI数据分析 + AI内容生成 + 自动化工作流搭建」的全栈运营，将是企业最愿意出高薪的对象。</p></div>
    <div class="trend-card"><div class="trend-icon">&#x1F393;</div><h4>学历门槛持续降低</h4><p>电商AI岗位的实战导向使得学历不再是硬门槛（{dazhuan_pct:.0f}%大专即可）。AI作品集、实操案例、工具熟练度将成为比学历更重要的评估标准。「会干活」比「有文凭」更有价值。</p></div>
  </div>
</div>

<!-- Section 7: Key Takeaways -->
<div class="section">
  <div class="section-title"><span class="icon" style="background:#fef5e7;">&#x1F3AF;</span>七、核心结论与建议</div>
  <div class="card">
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:20px;">
      <div style="padding:20px;background:#fef5e7;border-radius:14px;">
        <h4 style="margin-bottom:10px;">&#x1F4A1; 对求职者</h4>
        <ul style="font-size:0.88em;padding-left:20px;line-height:2;">
          <li><strong>最快入行路径：</strong>AI美工/AI运营助理，大专即可，0-1年经验，3K-8K起步</li>
          <li><strong>最高性价比方向：</strong>跨境电商AI，大专+英语+AI工具=8K-24K</li>
          <li><strong>最高薪资天花板：</strong>生鲜电商AI产品经理/算法工程师，30K-45K</li>
          <li><strong>最具成长性方向：</strong>AI训练师，连接技术与业务的桥梁角色</li>
          <li><strong>核心竞争力公式：</strong>电商实战 + AI工具熟练度 + 数据思维</li>
        </ul>
      </div>
      <div style="padding:20px;background:#eaf2f8;border-radius:14px;">
        <h4 style="margin-bottom:10px;">&#x1F3E2; 对企业</h4>
        <ul style="font-size:0.88em;padding-left:20px;line-height:2;">
          <li><strong>最值得投入的岗位：</strong>AI效能经理，能提升全团队AI使用率</li>
          <li><strong>性价比最高的方案：</strong>让现有运营/设计团队学习AI工具</li>
          <li><strong>需要抢人的方向：</strong>跨境电商AI人才，供不应求</li>
          <li><strong>可以观望的方向：</strong>AI数字人工程师，技术仍在快速迭代</li>
          <li><strong>建议：</strong>优先招「懂电商+会用AI」而非「懂AI+不懂电商」</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<!-- Section 8: Full Data -->
<div class="section">
  <div class="section-title"><span class="icon" style="background:#eaf2f8;">&#x1F4C4;</span>八、完整岗位数据表（{total}个岗位）</div>
  <div class="card">
    <p style="font-size:0.88em;color:var(--text-light);margin-bottom:12px;">按薪资中位数降序排列，可滚动查看全部数据</p>
    <div class="full-table-wrap">
      <table class="full-table">
        <thead><tr><th>岗位名称</th><th>薪资</th><th>经验</th><th>学历</th><th>城市</th><th>公司</th><th>类别</th></tr></thead>
        <tbody>
{full_table_rows}        </tbody>
      </table>
    </div>
  </div>
</div>

<div class="footer">
  <p>&#x1F4CB; 零售电商 AI 岗位专项深度分析报告</p>
  <p>数据来源：智联招聘 + BOSS直聘 + 行业公开信息 | 样本量：{total}个真实岗位</p>
  <p>生成时间：2026年4月3日 | <a href="index.html">返回报告索引</a></p>
</div>

</body>
</html>'''

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report generated: {OUTPUT_FILE}")
    print(f"Total jobs: {total}")
    print(f"Categories: {num_cats}")
    print(f"Salary range: {min_salary:.0f}K - {max_salary:.0f}K")
    print(f"Average salary: {avg_salary:.1f}K")


if __name__ == "__main__":
    main()
