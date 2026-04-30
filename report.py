from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Image, Table, TableStyle, HRFlowable)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os

# ── 注册中文字体 ──────────────────────────────────────────────
font_paths = [
    r'C:\Windows\Fonts\msyh.ttc',
    r'C:\Windows\Fonts\msyhbd.ttc',
]
try:
    pdfmetrics.registerFont(TTFont('MSYaHei', font_paths[0]))
    pdfmetrics.registerFont(TTFont('MSYaHei-Bold', font_paths[1]))
    FONT      = 'MSYaHei'
    FONT_BOLD = 'MSYaHei-Bold'
    print("✅ 中文字体加载成功")
except Exception as e:
    print(f"字体加载失败：{e}\n将使用默认字体（中文可能显示异常）")
    FONT = FONT_BOLD = 'Helvetica'

# ── 颜色定义 ──────────────────────────────────────────────────
BLUE       = colors.HexColor('#1E5FAD')
BLUE_LIGHT = colors.HexColor('#E8EEF7')
GRAY       = colors.HexColor('#595959')
GRAY_LIGHT = colors.HexColor('#F5F5F5')
WHITE      = colors.white
BLACK      = colors.HexColor('#1A1A1A')
GREEN      = colors.HexColor('#2ECC71')
ORANGE     = colors.HexColor('#F5A623')
RED        = colors.HexColor('#E74C3C')

W, H = A4  # 595 x 842 pt

# ── 文档初始化 ────────────────────────────────────────────────
OUTPUT = r'D:\archive\电商用户行为分析报告.pdf'
doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=2.2*cm, bottomMargin=2*cm
)

# ── 样式定义 ──────────────────────────────────────────────────
def style(name, font=FONT, size=10, color=BLACK, bold=False,
          align=TA_LEFT, leading=None, space_before=0, space_after=6):
    return ParagraphStyle(
        name,
        fontName=FONT_BOLD if bold else font,
        fontSize=size,
        textColor=color,
        alignment=align,
        leading=leading or size * 1.6,
        spaceBefore=space_before,
        spaceAfter=space_after,
    )

S_TITLE     = style('title',    size=22, color=WHITE,  bold=True, align=TA_CENTER, leading=30)
S_SUBTITLE  = style('subtitle', size=11, color=BLUE_LIGHT, align=TA_CENTER, leading=18)
S_META      = style('meta',     size=9,  color=BLUE_LIGHT, align=TA_CENTER)
S_H1        = style('h1',       size=13, color=BLUE,   bold=True, space_before=14, space_after=6)
S_H2        = style('h2',       size=10, color=BLUE,   bold=True, space_before=8,  space_after=4)
S_BODY      = style('body',     size=9.5,color=BLACK,  leading=17, space_after=5, align=TA_JUSTIFY)
S_BULLET    = style('bullet',   size=9.5,color=BLACK,  leading=17, space_after=3)
S_HIGHLIGHT = style('hl',       size=9.5,color=BLACK,  leading=17, space_after=5)
S_CAPTION   = style('caption',  size=8.5,color=GRAY,   align=TA_CENTER, space_after=10)
S_TAG       = style('tag',      size=9,  color=WHITE,  bold=True, align=TA_CENTER)

def HR(color=BLUE, thickness=1.2):
    return HRFlowable(width='100%', thickness=thickness,
                      color=color, spaceAfter=8, spaceBefore=4)

def chart(path, w_cm=14, caption=''):
    items = []
    if os.path.exists(path):
        img_w = w_cm * cm
        from PIL import Image as PILImage
        with PILImage.open(path) as im:
            ratio = im.height / im.width
        items.append(Image(path, width=img_w, height=img_w * ratio))
    if caption:
        items.append(Paragraph(caption, S_CAPTION))
    return items

def kpi_table(data):
    """data = [(label, value, note), ...]"""
    col_w = (W - 4*cm) / len(data)
    tdata = [[Paragraph(v[0], S_CAPTION),
              Paragraph(v[1], style('kv', size=18, color=BLUE, bold=True, align=TA_CENTER)),
              Paragraph(v[2], S_CAPTION)] for v in data]
    tdata_T = list(map(list, zip(*tdata)))  # transpose
    t = Table(tdata_T, colWidths=[col_w]*len(data))
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BLUE_LIGHT),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [BLUE_LIGHT, WHITE]),
        ('BOX',       (0,0), (-1,-1), 0.5, BLUE),
        ('INNERGRID', (0,0), (-1,-1), 0.3, colors.HexColor('#C8D6EA')),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING',   (0,0), (-1,-1), 6),
        ('RIGHTPADDING',  (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t

def insight_table(rows, col_widths=None):
    """通用两列表格：左标签右内容"""
    cw = col_widths or [3.5*cm, (W-4*cm-3.5*cm)]
    tdata = [[Paragraph(r[0], style('tlabel', size=9, color=WHITE, bold=True, align=TA_CENTER)),
              Paragraph(r[1], S_BODY)] for r in rows]
    t = Table(tdata, colWidths=cw)
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (0,-1), BLUE),
        ('BACKGROUND',    (1,0), (1,-1), WHITE),
        ('ROWBACKGROUNDS',(1,0), (1,-1), [WHITE, GRAY_LIGHT]),
        ('BOX',       (0,0), (-1,-1), 0.5, BLUE),
        ('INNERGRID', (0,0), (-1,-1), 0.3, colors.HexColor('#C8D6EA')),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t

# ════════════════════════════════════════════════════════════
# 开始构建内容
# ════════════════════════════════════════════════════════════
story = []

# ── 封面色块（用表格模拟）────────────────────────────────────
cover = Table(
    [[Paragraph('电商平台用户行为分析报告', S_TITLE)],
     [Spacer(1, 0.3*cm)],
     [Paragraph('基于美妆电商真实数据 | 用户转化漏斗 · 留存分析 · RFM用户分层', S_SUBTITLE)],
     [Spacer(1, 0.2*cm)],
     [Paragraph('数据来源：Kaggle eCommerce Events History &nbsp;|&nbsp; 分析周期：2019年10月 &nbsp;|&nbsp; 记录数：330万条', S_META)],
    ],
    colWidths=[W - 4*cm]
)
cover.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), BLUE),
    ('TOPPADDING',    (0,0), (-1,-1), 18),
    ('BOTTOMPADDING', (0,0), (-1,-1), 18),
    ('LEFTPADDING',   (0,0), (-1,-1), 20),
    ('RIGHTPADDING',  (0,0), (-1,-1), 20),
    ('ROUNDEDCORNERS', [6]),
]))
story.append(cover)
story.append(Spacer(1, 0.6*cm))

# ── 核心KPI ───────────────────────────────────────────────────
story.append(Paragraph('核心数据概览', S_H1))
story.append(HR())
story.append(kpi_table([
    ('涉及用户总数',  '39.9万',  '独立用户数'),
    ('行为记录总量',  '330万条', 'view/cart/purchase'),
    ('整体购买转化率','6.6%',   '浏览→最终购买'),
    ('新用户次日留存','6.6%',   '7日留存基准线'),
    ('购买用户数',   '2.58万',  '完成至少1次购买'),
]))
story.append(Spacer(1, 0.5*cm))

# ── 模块一：漏斗分析 ──────────────────────────────────────────
story.append(Paragraph('模块一：用户购买行为漏斗分析', S_H1))
story.append(HR())

story.append(Paragraph('1.1 漏斗数据', S_H2))
story.append(insight_table([
    ('浏览用户', '388,330 人 &nbsp;—&nbsp; 漏斗顶层，所有后续转化的基数'),
    ('加购用户', '133,715 人 &nbsp;—&nbsp; 浏览→加购转化率 <b>34.4%</b>，用户购买意向相对积极'),
    ('购买用户', '25,762 人 &nbsp;&nbsp;—&nbsp; 加购→购买转化率仅 <b>19.3%</b>，购物车流失严重'),
    ('整体转化', '整体转化率 <b>6.6%</b>，低于美妆电商行业均值（约8-12%），存在明显优化空间'),
]))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('1.2 漏斗图', S_H2))
story.extend(chart(r'D:\archive\chart1_funnel.png', w_cm=12,
                   caption='图1：用户购买行为漏斗（2019年10月）'))

story.append(Paragraph('1.3 核心洞察与运营建议', S_H2))
story.append(insight_table([
    ('核心痛点',
     '加购→购买流失率高达 <b>80.7%</b>（加购用户中仅约1/5最终完成购买）。'
     '用户已产生购买意向却未付款，属于典型"购物车放弃"问题，'
     '主要归因于：价格犹豫与比价行为、结账流程存在摩擦点、限时促销刺激不足。'),
    ('策略①',
     '<b>购物车挽回触达：</b>对加购超过24小时未购买的用户，触发自动化消息（站内信/短信/Push），'
     '内容包含商品提醒+限时优惠券（如9折），预计可将购物车转化率提升5-10pct。'),
    ('策略②',
     '<b>结账流程优化：</b>排查结账页面的跳出节点，简化支付步骤，'
     '增加"一键购买"功能，降低操作摩擦，减少因流程复杂导致的放弃。'),
    ('策略③',
     '<b>价格锚定优化：</b>在商品详情页展示"已有X人购买"、评价数量等社会证明信息，'
     '减少用户比价犹豫，增强购买决策信心。'),
]))
story.append(Spacer(1, 0.4*cm))

# ── 模块二：留存分析 ──────────────────────────────────────────
story.append(Paragraph('模块二：新用户7日留存分析', S_H1))
story.append(HR())

story.append(Paragraph('2.1 留存数据', S_H2))
story.append(insight_table([
    ('分析样本', '327,940 名新用户（2019年10月1日-24日首次出现，保证7天完整观察窗口）'),
    ('次日留存', '<b>6.6%</b> —— 仅有约1/15的新用户次日回访，用户粘性极低'),
    ('3日留存',  '<b>2.9%</b> —— 相比次日再度腰斩，说明第2-3天是关键流失窗口'),
    ('7日留存',  '<b>2.2%</b> —— 趋于平稳，核心用户群基本固化，但体量极小'),
    ('关键结论', '新用户次日留存断崖式下跌（6.6%→3.6%），<b>第1天是留存优化最高价值窗口</b>'),
]))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('2.2 留存曲线', S_H2))
story.extend(chart(r'D:\archive\chart2_retention.png', w_cm=13,
                   caption='图2：新用户7日留存曲线（2019年10月，基于327,940名新用户）'))

story.append(Paragraph('2.3 核心洞察与运营建议', S_H2))
story.append(insight_table([
    ('核心痛点',
     '次日留存仅 <b>6.6%</b>，远低于电商行业健康水平（通常20-35%）。'
     '超过93%的新用户在首次访问后第二天就不再回来，说明平台对新用户的承接与激活严重不足。'),
    ('策略①',
     '<b>新用户7日培育序列：</b>用户注册当天→第1天→第3天→第7天，'
     '设计自动化消息序列，内容分别为：平台使用引导、首购专属优惠、热销品推荐、积分到期提醒，'
     '目标将次日留存率提升至15%以上。'),
    ('策略②',
     '<b>首购激励设计：</b>对注册后48小时内未购买的新用户发放限时首购券（有效期72小时），'
     '制造紧迫感，推动完成首次交易。首购用户的长期留存率通常是未购买用户的3-5倍。'),
    ('策略③',
     '<b>个性化推荐优化：</b>基于用户首次浏览的品类偏好，首页和推送内容实时个性化，'
     '减少"看了半天没找到想要的"的认知成本，提升第二次访问意愿。'),
]))
story.append(Spacer(1, 0.4*cm))

# ── 模块三：用户分层 ──────────────────────────────────────────
story.append(Paragraph('模块三：RFM用户分层分析', S_H1))
story.append(HR())

story.append(Paragraph('3.1 分层方法说明', S_H2))
story.append(Paragraph(
    'RFM模型基于三个维度对购买用户进行分层：'
    '<b>R（Recency）</b>最近购买时间、<b>F（Frequency）</b>购买频次、<b>M（Monetary）</b>消费金额。'
    '本分析对购买用户（共25,762人）按R+F综合评分分为三层，'
    'M维度作为辅助验证指标。', S_BODY))
story.append(Spacer(1, 0.2*cm))

story.append(Paragraph('3.2 分层结果', S_H2))
story.append(insight_table([
    ('高价值用户',
     '<b>8,978人（34.8%）</b> —— 近期活跃、购买频次高，是平台营收的核心贡献群体，'
     '应重点维护，提供专属权益（如会员积分、优先客服、新品试用资格）防止流失。'),
    ('潜力用户',
     '<b>13,886人（53.9%）</b> —— 体量最大的机会池，有购买行为但频次或活跃度不足，'
     '是转化投入产出比最高的群体，适合定向促销和个性化推荐激活。'),
    ('流失风险用户',
     '<b>2,898人（11.2%）</b> —— 购买后长期未回访，需通过召回活动（大额优惠券、限时活动）'
     '尝试唤醒，若唤醒成本过高可降低运营资源投入。'),
]))
story.append(Spacer(1, 0.3*cm))

story.append(Paragraph('3.3 用户分层分布', S_H2))
story.extend(chart(r'D:\archive\chart3_rfm.png', w_cm=10,
                   caption='图3：购买用户RFM分层分布（2019年10月）'))

story.append(Paragraph('3.4 差异化运营策略矩阵', S_H2))
strategy = Table([
    [Paragraph('用户层级', style('th', size=9, color=WHITE, bold=True, align=TA_CENTER)),
     Paragraph('核心目标', style('th', size=9, color=WHITE, bold=True, align=TA_CENTER)),
     Paragraph('触达方式', style('th', size=9, color=WHITE, bold=True, align=TA_CENTER)),
     Paragraph('核心动作', style('th', size=9, color=WHITE, bold=True, align=TA_CENTER))],
    [Paragraph('高价值用户', S_BODY), Paragraph('防流失·提复购', S_BODY),
     Paragraph('专属客服·会员权益', S_BODY), Paragraph('新品首发权·积分翻倍·生日礼', S_BODY)],
    [Paragraph('潜力用户', S_BODY), Paragraph('促活跃·提频次', S_BODY),
     Paragraph('个性化Push·定向券', S_BODY), Paragraph('满减券·限时折扣·品类推荐', S_BODY)],
    [Paragraph('流失风险用户', S_BODY), Paragraph('召回·再激活', S_BODY),
     Paragraph('短信/邮件召回', S_BODY), Paragraph('大额券·限时活动·品类上新提醒', S_BODY)],
], colWidths=[3*cm, 3*cm, 3.5*cm, (W-4*cm-9.5*cm)])
strategy.setStyle(TableStyle([
    ('BACKGROUND',    (0,0), (-1,0), BLUE),
    ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, GRAY_LIGHT]),
    ('BOX',       (0,0), (-1,-1), 0.5, BLUE),
    ('INNERGRID', (0,0), (-1,-1), 0.3, colors.HexColor('#C8D6EA')),
    ('TOPPADDING',    (0,0), (-1,-1), 7),
    ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ('LEFTPADDING',   (0,0), (-1,-1), 8),
    ('RIGHTPADDING',  (0,0), (-1,-1), 8),
    ('ALIGN',  (0,0), (-1,0),  'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('FONTNAME', (0,0), (-1,0), FONT_BOLD),
]))
story.append(strategy)
story.append(Spacer(1, 0.5*cm))

# ── 总结 ──────────────────────────────────────────────────────
story.append(Paragraph('分析总结', S_H1))
story.append(HR())
story.append(insight_table([
    ('最高优先级',
     '<b>攻克购物车流失：</b>80.7%的加购用户最终未购买，这是转化率提升的最大单一机会，'
     '通过购物车挽回触达和结账流程优化，预计可将整体转化率从6.6%提升至8%+，'
     '接近行业均值水平。'),
    ('次高优先级',
     '<b>新用户首日激活：</b>次日留存仅6.6%说明新用户承接几乎缺失，'
     '建立7日培育序列是低成本高回报的留存杠杆，'
     '将次日留存提升至15%意味着回访用户数翻倍。'),
    ('长期策略',
     '<b>精细化用户分层运营：</b>53.9%的潜力用户是最大的增量机会池，'
     '通过差异化触达和个性化推荐将其中20%转化为高价值用户，'
     '可显著提升平台整体GMV与用户LTV。'),
]))
story.append(Spacer(1, 0.3*cm))

# ── 技术说明 ──────────────────────────────────────────────────
story.append(Paragraph('技术说明', S_H1))
story.append(HR())
tech = Table([
    [Paragraph('分析工具', S_BODY), Paragraph('Python 3.13 / Pandas / Matplotlib / Seaborn', S_BODY)],
    [Paragraph('数据来源', S_BODY), Paragraph('Kaggle：eCommerce Events History in Cosmetics Shop（公开数据集）', S_BODY)],
    [Paragraph('数据规模', S_BODY), Paragraph('原始数据410万条，清洗后334万条有效记录，涉及39.9万独立用户', S_BODY)],
    [Paragraph('分析周期', S_BODY), Paragraph('2019年10月1日 – 2019年10月31日（完整自然月）', S_BODY)],
    [Paragraph('代码仓库', S_BODY), Paragraph('GitHub：[你的GitHub链接]', S_BODY)],
], colWidths=[3*cm, W-4*cm-3*cm])
tech.setStyle(TableStyle([
    ('ROWBACKGROUNDS', (0,0), (-1,-1), [BLUE_LIGHT, WHITE]),
    ('BOX',       (0,0), (-1,-1), 0.5, BLUE),
    ('INNERGRID', (0,0), (-1,-1), 0.3, colors.HexColor('#C8D6EA')),
    ('TOPPADDING',    (0,0), (-1,-1), 7),
    ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ('LEFTPADDING',   (0,0), (-1,-1), 8),
    ('RIGHTPADDING',  (0,0), (-1,-1), 8),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('FONTNAME', (0,0), (0,-1), FONT_BOLD),
]))
story.append(tech)

# ── 生成PDF ───────────────────────────────────────────────────
print("\n正在生成PDF报告...")
doc.build(story)
print(f"✅ 报告生成成功：{OUTPUT}")