import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.patches as mpatches
import numpy as np
import warnings
warnings.filterwarnings('ignore')

matplotlib.rcParams['font.family'] = 'Microsoft YaHei'
matplotlib.rcParams['axes.unicode_minus'] = False

# ── 读取清洗后的数据 ──────────────────────────────────────────
print("读取数据中...")
df = pd.read_csv(r'D:\archive\cleaned.csv')
df['event_time'] = pd.to_datetime(df['event_time'])
df['date'] = pd.to_datetime(df['date']).dt.date
print(f"加载完成，共 {len(df):,} 条记录")

# ════════════════════════════════════════════════════════════
# 模块1：用户行为漏斗
# 逻辑：统计"至少做过该行为一次"的独立用户数，计算各环节转化率
# ════════════════════════════════════════════════════════════
print("\n正在计算漏斗数据...")

users_view     = df[df['event_type'] == 'view']['user_id'].nunique()
users_cart     = df[df['event_type'] == 'cart']['user_id'].nunique()
users_purchase = df[df['event_type'] == 'purchase']['user_id'].nunique()

# 各环节转化率
rate_view_to_cart     = users_cart / users_view * 100
rate_cart_to_purchase = users_purchase / users_cart * 100
rate_overall          = users_purchase / users_view * 100

print(f"\n=== 用户行为漏斗 ===")
print(f"浏览用户数：     {users_view:>8,}")
print(f"加购用户数：     {users_cart:>8,}  (浏览→加购转化率：{rate_view_to_cart:.1f}%)")
print(f"购买用户数：     {users_purchase:>8,}  (加购→购买转化率：{rate_cart_to_purchase:.1f}%)")
print(f"整体转化率：     {rate_overall:.1f}%")

# 绘制漏斗图
fig, ax = plt.subplots(figsize=(8, 6))
fig.patch.set_facecolor('#F8F9FA')
ax.set_facecolor('#F8F9FA')

stages  = ['浏览用户', '加购用户', '购买用户']
values  = [users_view, users_cart, users_purchase]
colors  = ['#4A90D9', '#F5A623', '#E74C3C']
max_val = values[0]
bar_h   = 0.5
gap     = 0.25

for i, (stage, val, color) in enumerate(zip(stages, values, colors)):
    width = val / max_val
    left  = (1 - width) / 2
    y     = (len(stages) - 1 - i) * (bar_h + gap)
    ax.barh(y, width, left=left, height=bar_h, color=color, alpha=0.88)
    ax.text(0.5, y, f"{stage}\n{val:,} 人", ha='center', va='center',
            fontsize=12, fontweight='bold', color='white')
    if i < len(stages) - 1:
        next_val = values[i + 1]
        rate     = next_val / val * 100
        ax.text(1.02, y - (bar_h + gap) / 2,
                f"↓ {rate:.1f}%", va='center', fontsize=11,
                color='#555555', fontweight='bold')

ax.set_xlim(0, 1.15)
ax.axis('off')
ax.set_title('用户购买行为漏斗分析（2019年10月）',
             fontsize=15, fontweight='bold', pad=15, color='#2C3E50')
plt.tight_layout()
plt.savefig(r'D:\archive\chart1_funnel.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ 漏斗图已保存：chart1_funnel.png")

# ════════════════════════════════════════════════════════════
# 模块2：新用户7日留存分析
# 逻辑：找出每个用户第一次出现的日期，统计之后7天内是否回访
# ════════════════════════════════════════════════════════════
print("\n正在计算留存数据（稍慢，约30秒）...")

# 每个用户的首次行为日期
first_date = df.groupby('user_id')['date'].min().reset_index()
first_date.columns = ['user_id', 'first_date']

# 只取10月1日-10月24日首次出现的用户（保证有7天观察窗口）
import datetime
cutoff = datetime.date(2019, 10, 24)
new_users = first_date[first_date['first_date'] <= cutoff].copy()

# 合并用户的所有行为日期
user_dates = df.groupby('user_id')['date'].apply(set).reset_index()
user_dates.columns = ['user_id', 'date_set']
new_users = new_users.merge(user_dates, on='user_id')

# 计算每天留存率
retention = {}
for day in range(1, 8):
    def came_back(row):
        target = row['first_date'] + datetime.timedelta(days=day)
        return target in row['date_set']
    came_back_count = new_users.apply(came_back, axis=1).sum()
    retention[f'第{day}天'] = came_back_count / len(new_users) * 100

print(f"\n=== 新用户7日留存率（基于 {len(new_users):,} 名新用户）===")
for k, v in retention.items():
    bar = '█' * int(v / 2)
    print(f"  {k}：{v:5.1f}%  {bar}")

# 绘制留存曲线
fig, ax = plt.subplots(figsize=(9, 5))
fig.patch.set_facecolor('#F8F9FA')
ax.set_facecolor('#F8F9FA')

days  = list(retention.keys())
rates = list(retention.values())

ax.plot(days, rates, color='#4A90D9', linewidth=2.5,
        marker='o', markersize=8, markerfacecolor='white',
        markeredgecolor='#4A90D9', markeredgewidth=2.5)

for x, y in zip(days, rates):
    ax.annotate(f'{y:.1f}%', (x, y),
                textcoords="offset points", xytext=(0, 12),
                ha='center', fontsize=10, color='#2C3E50', fontweight='bold')

ax.fill_between(days, rates, alpha=0.12, color='#4A90D9')
ax.set_ylim(0, max(rates) * 1.3)
ax.set_xlabel('注册后第N天', fontsize=12, color='#555')
ax.set_ylabel('留存率 (%)', fontsize=12, color='#555')
ax.set_title('新用户7日留存曲线（2019年10月）',
             fontsize=15, fontweight='bold', pad=15, color='#2C3E50')
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig(r'D:\archive\chart2_retention.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ 留存图已保存：chart2_retention.png")

# ════════════════════════════════════════════════════════════
# 模块3：用户分层（RFM简化版）
# ════════════════════════════════════════════════════════════
print("\n正在计算用户分层...")

purchase_df = df[df['event_type'] == 'purchase'].copy()
purchase_df['date'] = pd.to_datetime(purchase_df['date'])
snapshot_date = pd.Timestamp('2019-11-01')

rfm = purchase_df.groupby('user_id').agg(
    recency   = ('date', lambda x: (snapshot_date - x.max()).days),
    frequency = ('product_id', 'count'),
    monetary  = ('price', 'sum')
).reset_index()

# 打分（1-3分）
rfm['r_score'] = pd.qcut(rfm['recency'],   q=3, labels=[3, 2, 1]).astype(int)
rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'),
                          q=3, labels=[1, 2, 3]).astype(int)
rfm['total']   = rfm['r_score'] + rfm['f_score']

def segment(score):
    if score >= 5: return '高价值用户'
    elif score >= 3: return '潜力用户'
    else: return '流失风险用户'

rfm['segment'] = rfm['total'].apply(segment)

seg_counts = rfm['segment'].value_counts()
seg_pct    = rfm['segment'].value_counts(normalize=True) * 100

print(f"\n=== 用户分层结果（购买用户共 {len(rfm):,} 人）===")
for seg in seg_counts.index:
    print(f"  {seg}：{seg_counts[seg]:,} 人（{seg_pct[seg]:.1f}%）")

# 绘制用户分层饼图
fig, ax = plt.subplots(figsize=(7, 6))
fig.patch.set_facecolor('#F8F9FA')
ax.set_facecolor('#F8F9FA')

colors_pie = ['#2ECC71', '#F5A623', '#E74C3C']
wedges, texts, autotexts = ax.pie(
    seg_counts.values,
    labels=seg_counts.index,
    autopct='%1.1f%%',
    colors=colors_pie,
    startangle=140,
    pctdistance=0.75,
    wedgeprops={'edgecolor': 'white', 'linewidth': 2}
)
for text in texts:
    text.set_fontsize(12)
for autotext in autotexts:
    autotext.set_fontsize(11)
    autotext.set_fontweight('bold')
    autotext.set_color('white')

ax.set_title('购买用户RFM分层分布（2019年10月）',
             fontsize=15, fontweight='bold', pad=15, color='#2C3E50')
plt.tight_layout()
plt.savefig(r'D:\archive\chart3_rfm.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ 用户分层图已保存：chart3_rfm.png")

print("\n🎉 全部分析完成！三张图表已保存至 D:\\archive\\")