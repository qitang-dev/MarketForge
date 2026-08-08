from pathlib import Path

import numpy as np
import pandas as pd

# ============================================================
# Project configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROFILE_PATH = (
    PROJECT_ROOT
    / "integrated_analysis"
    / "data"
    / "processed"
    / "stock_profiles_2025.csv"
)

TABLE_OUTPUT_DIRECTORY = (
    PROJECT_ROOT / "integrated_analysis" / "data" / "output" / "tables"
)

REPORT_OUTPUT_DIRECTORY = (
    PROJECT_ROOT / "integrated_analysis" / "data" / "output" / "reports"
)

SUMMARY_TABLE_PATH = TABLE_OUTPUT_DIRECTORY / "stock_summary_table.csv"

FINAL_REPORT_PATH = REPORT_OUTPUT_DIRECTORY / "final_analysis.md"


ANALYSIS_YEAR = 2025


# ============================================================
# Translation maps
# ============================================================

VALUATION_PROFILE_MAP = {
    "relatively_low_valuation": "相对低估值",
    "mid_valuation": "中等估值",
    "relatively_high_valuation": "相对高估值",
    "loss_making_pe": "市盈率为负（亏损状态）",
    "unavailable": "估值数据不足",
}


ACTIVITY_PROFILE_MAP = {
    "high_activity": "高活跃",
    "moderate_activity": "中等活跃",
    "low_activity": "低活跃",
    "unavailable": "活跃度数据不足",
}


LIMIT_PROFILE_MAP = {
    "strong_limit_activity": "涨停事件特征较强",
    "moderate_limit_activity": "涨停事件特征中等",
    "low_limit_activity": "涨停事件特征较弱",
    "unavailable": "涨停事件数据不足",
}


CONSOLIDATION_PROFILE_MAP = {
    "consolidation_dominant": "整理结构占主导",
    "mixed_structure": "趋势与整理混合",
    "trend_dominant": "趋势结构占主导",
    "unavailable": "整理结构数据不足",
}


MARKET_STYLE_MAP = {
    "active_trending": "高活跃趋势型",
    "active_mixed": "高活跃混合型",
    "active_consolidating": "高活跃整理型",
    "moderate_trending": "中等活跃趋势型",
    "balanced": "均衡型",
    "moderate_consolidating": "中等活跃整理型",
    "quiet_trending": "低活跃趋势型",
    "quiet_mixed": "低活跃混合型",
    "quiet_consolidating": "低活跃整理型",
    "unavailable": "交易风格数据不足",
}


GROWTH_PROFILE_MAP = {
    "strong_growth": "高增长",
    "moderate_growth": "中等增长",
    "weak_growth": "低增长",
    "unavailable": "增长数据不足",
}


PROFITABILITY_PROFILE_MAP = {
    "high_profitability": "高盈利能力",
    "moderate_profitability": "中等盈利能力",
    "low_profitability": "低盈利能力",
    "unavailable": "盈利能力数据不足",
}


# ============================================================
# Utility functions
# ============================================================


def load_profile_data() -> pd.DataFrame:
    print(f"[LOAD] Profile data: " f"{PROFILE_PATH}")

    if not PROFILE_PATH.exists():
        raise FileNotFoundError(f"Profile data not found: " f"{PROFILE_PATH}")

    data = pd.read_csv(
        PROFILE_PATH,
        encoding="utf-8-sig",
        dtype={
            "stock_code": str,
        },
    )

    data.columns = data.columns.astype(str).str.strip()

    data = data.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    return data


def format_percent(
    value,
    digits: int = 2,
) -> str:
    if pd.isna(value):
        return "N/A"

    return f"{float(value) * 100:.{digits}f}%"


def format_number(
    value,
    digits: int = 2,
) -> str:
    if pd.isna(value):
        return "N/A"

    return f"{float(value):.{digits}f}"


def format_integer(
    value,
) -> str:
    if pd.isna(value):
        return "N/A"

    return str(int(round(float(value))))


def map_value(
    value,
    mapping: dict,
) -> str:
    if pd.isna(value):
        return "数据不足"

    return mapping.get(
        str(value),
        str(value),
    )


# ============================================================
# Summary descriptions
# ============================================================


def describe_fundamentals(
    row: pd.Series,
) -> str:
    growth = map_value(
        row.get("growth_profile"),
        GROWTH_PROFILE_MAP,
    )

    profitability = map_value(
        row.get("profitability_profile"),
        PROFITABILITY_PROFILE_MAP,
    )

    roe = format_percent(row.get("roe"))

    revenue_yoy = format_percent(row.get("revenue_yoy"))

    profit_yoy = format_percent(row.get("parent_net_profit_yoy"))

    return (
        f"{growth}、{profitability}；"
        f"营收同比 {revenue_yoy}，"
        f"归母净利润同比 {profit_yoy}，"
        f"ROE {roe}"
    )


def describe_valuation(
    row: pd.Series,
) -> str:
    profile = map_value(
        row.get("valuation_profile"),
        VALUATION_PROFILE_MAP,
    )

    pe = row.get("pe_ttm_median")

    pb = row.get("pb_median")

    if pd.notna(pe) and pe > 0:
        pe_text = f"PE(TTM)中位数 " f"{format_number(pe)}"

    elif pd.notna(pe):
        pe_text = "PE(TTM)为负，" "反映样本期存在亏损"

    else:
        pe_text = "PE数据不足"

    pb_text = f"PB中位数 " f"{format_number(pb)}"

    return f"{profile}；" f"{pe_text}，" f"{pb_text}"


def describe_activity(
    row: pd.Series,
) -> str:
    relative_activity = map_value(
        row.get("relative_activity_profile"),
        ACTIVITY_PROFILE_MAP,
    )

    market_style = map_value(
        row.get("market_style"),
        MARKET_STYLE_MAP,
    )

    volatility = format_percent(row.get("annualized_volatility"))

    turnover = row.get("average_turnover")

    turnover_text = format_number(turnover)

    large_move_rate = format_percent(row.get("large_move_rate"))

    volume_surge_rate = format_percent(row.get("volume_surge_rate"))

    return (
        f"{relative_activity}，"
        f"交易风格为{market_style}；"
        f"年化波动率 {volatility}，"
        f"平均换手率 {turnover_text}，"
        f"大幅波动日占比 {large_move_rate}，"
        f"放量日占比 {volume_surge_rate}"
    )


def describe_limit_events(
    row: pd.Series,
) -> str:
    profile = map_value(
        row.get("limit_event_profile"),
        LIMIT_PROFILE_MAP,
    )

    limit_up_count = format_integer(row.get("limit_up_count"))

    limit_down_count = format_integer(row.get("limit_down_count"))

    failed_limit_rate = format_percent(row.get("failed_limit_up_rate"))

    maximum_consecutive = format_integer(row.get("maximum_consecutive_limit_up_days"))

    return (
        f"{profile}；"
        f"全年涨停 {limit_up_count} 次，"
        f"跌停 {limit_down_count} 次，"
        f"炸板率 {failed_limit_rate}，"
        f"最大连续涨停 "
        f"{maximum_consecutive} 天"
    )


def describe_consolidation(
    row: pd.Series,
) -> str:
    profile = map_value(
        row.get("consolidation_profile"),
        CONSOLIDATION_PROFILE_MAP,
    )

    day_rate = format_percent(row.get("consolidation_day_rate"))

    average_duration = format_number(
        row.get("average_duration_days"),
        digits=1,
    )

    average_box_range = format_percent(row.get("average_box_range"))

    active_count = format_integer(row.get("active_consolidation_count"))

    moderate_count = format_integer(row.get("moderate_consolidation_count"))

    mild_count = format_integer(row.get("mild_consolidation_count"))

    return (
        f"{profile}；"
        f"整理交易日占比 {day_rate}，"
        f"平均整理周期 "
        f"{average_duration} 个交易日，"
        f"平均箱体振幅 "
        f"{average_box_range}；"
        f"活跃/中等/温和整理次数分别为 "
        f"{active_count}/"
        f"{moderate_count}/"
        f"{mild_count}"
    )


def describe_possible_capital_behavior(
    row: pd.Series,
) -> str:
    activity_score = row.get("activity_score")

    limit_score = row.get("limit_event_score")

    consolidation_score = row.get("consolidation_score")

    if pd.isna(activity_score) or pd.isna(limit_score) or pd.isna(consolidation_score):
        return "现有数据不足以形成完整的" "资金行为特征判断。"

    if activity_score >= 0.67 and limit_score >= 0.67:
        return (
            "量价活跃度和涨停事件均处于"
            "样本较高水平，呈现较强的"
            "短期资金推动和事件驱动特征；"
            "该特征仅反映交易行为，"
            "不能据此证明存在特定主力操纵。"
        )

    if activity_score >= 0.67 and consolidation_score >= 0.67:
        return (
            "整理阶段内部仍保持较高交易活跃度，"
            "呈现活跃震荡特征，"
            "可能反映较频繁的资金博弈。"
        )

    if activity_score < 0.33 and consolidation_score >= 0.67:
        return (
            "较长时间处于低波动整理状态，"
            "箱体运行相对温和，"
            "更接近低活跃、缓慢整理的"
            "交易行为特征。"
        )

    if consolidation_score < 0.33 and activity_score >= 0.67:
        return (
            "趋势运行特征明显且交易活跃，"
            "相比长期箱体整理，"
            "价格更容易出现快速方向性运动。"
        )

    if limit_score >= 0.67:
        return (
            "涨停及相关事件较为突出，"
            "价格行为具有一定事件驱动特征，"
            "但不足以据此判断具体资金主体。"
        )

    return "交易行为整体较为均衡，" "未观察到单一特征长期占据绝对主导。"


# ============================================================
# Build summary table
# ============================================================


def build_summary_table(
    data: pd.DataFrame,
) -> pd.DataFrame:
    result = pd.DataFrame()

    result["stock_code"] = data["stock_code"]

    result["stock_name"] = data["stock_name"]

    result["fundamental_summary"] = data.apply(
        describe_fundamentals,
        axis=1,
    )

    result["valuation_summary"] = data.apply(
        describe_valuation,
        axis=1,
    )

    result["activity_summary"] = data.apply(
        describe_activity,
        axis=1,
    )

    result["limit_event_summary"] = data.apply(
        describe_limit_events,
        axis=1,
    )

    result["consolidation_summary"] = data.apply(
        describe_consolidation,
        axis=1,
    )

    result["capital_behavior_summary"] = data.apply(
        describe_possible_capital_behavior,
        axis=1,
    )

    result["market_style"] = data["market_style"].map(
        lambda value: map_value(
            value,
            MARKET_STYLE_MAP,
        )
    )

    result["fundamental_score"] = data["fundamental_score"]

    result["activity_score"] = data["activity_score"]

    result["consolidation_score"] = data["consolidation_score"]

    result = result.sort_values(
        by="fundamental_score",
        ascending=False,
    ).reset_index(drop=True)

    return result


# ============================================================
# Markdown helpers
# ============================================================


def get_top_stocks(
    data: pd.DataFrame,
    column: str,
    count: int = 3,
    ascending: bool = False,
) -> pd.DataFrame:
    valid = data.dropna(subset=[column])

    return valid.sort_values(
        by=column,
        ascending=ascending,
    ).head(count)


def stock_names_text(
    data: pd.DataFrame,
) -> str:
    return "、".join(data["stock_name"].astype(str).tolist())


# ============================================================
# Generate markdown report
# ============================================================


def generate_markdown_report(
    data: pd.DataFrame,
    summary_table: pd.DataFrame,
) -> str:
    top_fundamental = get_top_stocks(
        data=data,
        column="fundamental_score",
    )

    top_activity = get_top_stocks(
        data=data,
        column="activity_score",
    )

    top_consolidation = get_top_stocks(
        data=data,
        column="consolidation_score",
    )

    low_consolidation = get_top_stocks(
        data=data,
        column="consolidation_score",
        ascending=True,
    )

    high_limit = get_top_stocks(
        data=data,
        column="limit_event_score",
    )

    negative_pe_data = data[data["valuation_profile"] == "loss_making_pe"]

    report_lines: list[str] = []

    report_lines.extend(
        [
            "# A股样本公司综合量化分析报告",
            "",
            f"**分析年度：{ANALYSIS_YEAR} 年**",
            "",
            (f"**样本数量：{len(data)} 家上市公司**"),
            "",
            "---",
            "",
            "## 一、分析目的",
            "",
            (
                "本报告基于样本公司财务报表、"
                "历史估值、日度量价数据以及涨跌停事件数据，"
                "对样本公司的基本面、估值水平、"
                "股票活跃度、涨跌停特征和横盘整理结构"
                "进行综合分析。"
            ),
            "",
            ("分析重点对应以下四个方面："),
            "",
            (
                "1. 年报、季报中的营业收入、净利润、"
                "盈利能力及市盈率、市净率等基本面与估值指标；"
            ),
            (
                "2. 基于成交量、换手率、波动率、"
                "大幅涨跌和放量行为分析股票股性与活跃程度；"
            ),
            ("3. 统计年度涨停、跌停、炸板、" "连续涨停以及涨停后的价格表现；"),
            (
                "4. 识别横盘箱体和震荡整理区间，"
                "比较不同股票的活跃震荡与温和整理特征。"
            ),
            "",
            (
                "> 注：本报告中的“资金行为”仅指"
                "由公开量价数据推断出的交易行为特征。"
                "成交量、换手率、涨停和价格波动本身"
                "不能证明某一特定资金主体存在操纵、"
                "洗盘或控盘行为。"
            ),
            "",
            "---",
            "",
            "## 二、数据与方法",
            "",
            "### 2.1 基本面数据",
            "",
            (
                "基本面数据来自样本公司的资产负债表、"
                "利润表和现金流量表。主要分析指标包括"
                "营业收入及同比增速、归母净利润及同比增速、"
                "毛利率、净利率、ROE、资产负债率、"
                "流动比率、总资产增速和经营现金流质量等。"
            ),
            "",
            (
                "综合基本面评分采用样本内百分位排名，"
                "用于比较 16 家样本公司之间的相对位置，"
                "不代表绝对意义上的公司质量评分。"
            ),
            "",
            "### 2.2 估值数据",
            "",
            (
                "估值指标主要包括 PE(TTM)、静态 PE、"
                "PB 和总市值。估值数据按照真实交易日进行过滤，"
                "避免自然日重复数据对年度均值造成额外权重。"
            ),
            "",
            (
                "对于 PE 小于或等于 0 的公司，"
                "报告单独标记为亏损状态，"
                "不将负 PE 解释为低估值。"
            ),
            "",
            "### 2.3 股票活跃度",
            "",
            (
                "股票活跃度主要参考年化波动率、平均换手率、"
                "大幅涨跌日比例、放量日比例、"
                "成交量相对 20 日均值和换手率相对历史水平等指标。"
            ),
            "",
            (
                "根据这些指标构建样本内相对活跃度评分，"
                "用于区分高活跃、中等活跃和低活跃股票。"
            ),
            "",
            "### 2.4 涨跌停事件",
            "",
            (
                "涨跌停分析统计全年涨停次数、跌停次数、"
                "一字涨停、炸板和连续涨停情况，"
                "并观察涨停后次日开盘、收盘以及"
                "后续 3 个和 5 个交易日的表现。"
            ),
            "",
            "### 2.5 横盘整理与交易风格",
            "",
            (
                "横盘整理识别采用 20 个交易日滚动窗口，"
                "综合价格箱体宽度、均线收敛程度、"
                "MA20 斜率和滚动波动率判断候选整理状态。"
            ),
            "",
            (
                "连续候选交易日进一步受到固定箱体约束，"
                "并要求有效整理周期不少于 8 个交易日。"
                "整理阶段根据日内振幅、相对成交量和"
                "相对换手率划分为活跃、中等和温和整理。"
            ),
            "",
            "---",
            "",
            "## 三、基本面与估值分析",
            "",
            (
                "从样本内综合基本面评分来看，"
                f"{stock_names_text(top_fundamental)} "
                "处于样本前列。"
            ),
            "",
        ]
    )

    if not negative_pe_data.empty:
        report_lines.extend(
            [
                (
                    f"{stock_names_text(negative_pe_data)} "
                    "在样本期内 PE(TTM) 中位数为负或"
                    "处于亏损状态，因此在估值分析中"
                    "单独列示，而不按照传统正 PE 框架"
                    "解释为低估值。"
                ),
                "",
            ]
        )

    report_lines.extend(
        [
            (
                "需要注意，不同行业公司的资本结构、"
                "盈利模式和合理估值区间存在明显差异，"
                "因此本报告中的估值高低主要反映"
                "当前 16 家样本公司的横截面相对位置，"
                "不等同于投资价值判断。"
            ),
            "",
            "---",
            "",
            "## 四、股票活跃度与量价特征",
            "",
            (
                "按照综合活跃度评分，"
                f"{stock_names_text(top_activity)} "
                "处于样本中较高水平。"
            ),
            "",
            (
                "高活跃股票通常表现为较高波动率、"
                "较频繁的大幅涨跌、放量或换手率异常；"
                "低活跃股票则更多表现为较低波动和"
                "较长时间的稳定运行。"
            ),
            "",
            (
                "这些特征可以用于描述股票的交易性格，"
                "但不能仅依据高换手、高成交量或价格异动"
                "判断存在特定主力资金。"
            ),
            "",
            "---",
            "",
            "## 五、年度涨跌停及涨停后表现",
            "",
            (
                "从涨停事件综合特征来看，"
                f"{stock_names_text(high_limit)} "
                "在样本中具有较明显的涨停或连续涨停特征。"
            ),
            "",
            (
                "除涨停次数外，本项目还记录炸板率、"
                "最大连续涨停天数以及涨停后 1、3、5 个"
                "交易日表现，因此可以进一步判断涨停后的"
                "价格延续性和回撤风险。"
            ),
            "",
            (
                "涨停频繁并不意味着股票表现更优。"
                "部分股票可能在涨停后继续上涨，"
                "也可能快速回撤，因此需要结合"
                "后续收益和最大回撤综合观察。"
            ),
            "",
            "---",
            "",
            "## 六、横盘整理与交易风格",
            "",
            (
                f"{stock_names_text(top_consolidation)} "
                "的整理结构在样本中相对突出，"
                "较多交易日处于低趋势、箱体或"
                "均线收敛状态。"
            ),
            "",
            (
                f"{stock_names_text(low_consolidation)} "
                "的整理结构相对较弱，"
                "更多时间呈现趋势运行或较活跃的价格变化。"
            ),
            "",
            (
                "整理阶段进一步按照成交活跃程度划分为"
                "活跃整理、中等整理和温和整理。"
                "其中活跃整理通常伴随较明显的日内振幅、"
                "放量或换手变化；温和整理则主要表现为"
                "低波动和相对稳定的箱体结构。"
            ),
            "",
            (
                "这一分类可以用于研究不同股票的交易行为风格，"
                "但“横盘整理”或“活跃震荡”本身"
                "不能直接证明存在所谓洗盘行为。"
            ),
            "",
            "---",
            "",
            "## 七、综合交易风格分类",
            "",
            ("综合活跃度和整理结构后，" "本项目将股票交易风格划分为："),
            "",
            "- 高活跃趋势型（active_trending）",
            "- 高活跃混合型（active_mixed）",
            "- 高活跃整理型（active_consolidating）",
            "- 中等活跃趋势型（moderate_trending）",
            "- 均衡型（balanced）",
            "- 中等活跃整理型（moderate_consolidating）",
            "- 低活跃趋势型（quiet_trending）",
            "- 低活跃混合型（quiet_mixed）",
            "- 低活跃整理型（quiet_consolidating）",
            "",
            ("该分类重点描述交易行为，而不是" "对股票进行投资意义上的优劣排序。"),
            "",
            "---",
            "",
            "## 八、样本公司逐股总结",
            "",
        ]
    )

    for _, row in summary_table.iterrows():
        report_lines.extend(
            [
                (f"### {row['stock_name']} " f"（{row['stock_code']}）"),
                "",
                (f"- **基本面：** " f"{row['fundamental_summary']}"),
                (f"- **估值：** " f"{row['valuation_summary']}"),
                (f"- **股性与活跃度：** " f"{row['activity_summary']}"),
                (f"- **涨跌停事件：** " f"{row['limit_event_summary']}"),
                (f"- **横盘与震荡：** " f"{row['consolidation_summary']}"),
                (f"- **交易行为特征：** " f"{row['capital_behavior_summary']}"),
                "",
            ]
        )

    report_lines.extend(
        [
            "---",
            "",
            "## 九、主要结论",
            "",
            (
                "1. 样本股票在基本面、估值和交易行为上"
                "存在明显差异，因此不能仅使用单一指标"
                "描述股票特征。"
            ),
            "",
            (
                "2. 基本面质量和股票交易活跃程度"
                "并不存在简单的一一对应关系。"
                "基本面较强的公司可能交易风格平稳，"
                "而高活跃股票也不一定具有较高基本面评分。"
            ),
            "",
            (
                "3. 涨停次数、连续涨停和炸板等指标"
                "能够反映股票的事件驱动和短期交易特征，"
                "但需要结合涨停后的收益和回撤判断"
                "价格行为是否具有延续性。"
            ),
            "",
            (
                "4. 横盘整理结构能够有效区分"
                "长期箱体型股票与趋势运行型股票。"
                "结合成交量、换手率和日内振幅，"
                "还可以进一步区分活跃震荡和温和整理。"
            ),
            "",
            (
                "5. 公开量价数据可以用于识别"
                "异常活跃、持续放量、频繁涨停和"
                "长期箱体等交易行为特征，"
                "但不足以单独证明某一特定主体的"
                "建仓、洗盘、控盘或操纵行为。"
            ),
            "",
            "---",
            "",
            "## 十、项目局限性",
            "",
            (
                "本项目目前主要基于公开财务数据、"
                "估值数据和日度市场数据。"
                "由于历史资金流接口存在连接问题，"
                "资金流数据未作为本阶段分析的核心输入。"
            ),
            "",
            (
                "此外，涨跌停判断采用当前样本适用的"
                "简化涨跌停规则，未单独恢复每只股票"
                "在历史日期上的 ST 状态。"
                "因此相关结果适合作为量化研究和"
                "横截面比较使用，而不应解释为"
                "交易所级别的历史事件审计结果。"
            ),
            "",
            (
                "不同公司所属行业存在明显差异，"
                "PE、PB、ROE、利润率等指标的合理区间"
                "也存在行业差异。后续若扩大项目规模，"
                "可进一步加入行业分类和行业内相对比较。"
            ),
            "",
            "---",
            "",
            "## 十一、总结",
            "",
            (
                "本项目已经完成从公开数据获取、"
                "数据清洗、财务因子构建、估值整理、"
                "量价特征提取、涨跌停事件分析、"
                "横盘箱体识别到综合股票画像的完整流程。"
            ),
            "",
            (
                "最终结果能够从基本面、估值、"
                "股性、涨跌停行为和横盘震荡风格"
                "五个角度对 16 家样本公司进行"
                "较系统的横截面比较，"
                "基本覆盖本阶段研究目标。"
            ),
            "",
        ]
    )

    return "\n".join(report_lines)


# ============================================================
# Main
# ============================================================


def main() -> None:
    TABLE_OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("\n========== " "GENERATE FINAL ANALYSIS SUMMARY " "==========")

    data = load_profile_data()

    summary_table = build_summary_table(data=data)

    summary_table.to_csv(
        SUMMARY_TABLE_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"[SAVED] Summary table: " f"{SUMMARY_TABLE_PATH}")

    markdown_report = generate_markdown_report(
        data=data,
        summary_table=(summary_table),
    )

    FINAL_REPORT_PATH.write_text(
        markdown_report,
        encoding="utf-8",
    )

    print(f"[SAVED] Final report: " f"{FINAL_REPORT_PATH}")

    print("\n========== " "SUMMARY PREVIEW " "==========")

    preview_columns = [
        "stock_code",
        "stock_name",
        "market_style",
        "fundamental_score",
        "activity_score",
        "consolidation_score",
    ]

    print(summary_table[preview_columns].to_string(index=False))

    print("\n========== " "PROCESSING RESULT " "==========")

    print(f"Stocks summarized: " f"{len(summary_table)}")

    print("Final analysis summary " "generated successfully.")


if __name__ == "__main__":
    main()
