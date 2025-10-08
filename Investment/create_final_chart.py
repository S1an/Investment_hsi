import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def _add_investment_zones(ax1, ax2, monthly_df):
    """
    基于M2同比增长率添加竖向投资区域划分
    """
    # 获取恒生指数Y轴范围
    y_min_hsi = ax1.get_ylim()[0]
    y_max_hsi = ax1.get_ylim()[1]
    
    # 定义区域阈值（基于M2同比增长率）- 按照投资周期顺序：建仓-加仓-减仓-清仓-观望
    zones = [
        {"name": "建仓期", "m2_min": 12, "m2_max": float('inf'), "color": "lightcoral", "alpha": 0.2},
        {"name": "加仓期", "m2_min": 8, "m2_max": 12, "color": "lightpink", "alpha": 0.15},
        {"name": "减仓期", "m2_min": 4, "m2_max": 8, "color": "lightgreen", "alpha": 0.15},
        {"name": "清仓期", "m2_min": 0, "m2_max": 4, "color": "lightblue", "alpha": 0.2},
        {"name": "观望期", "m2_min": float('-inf'), "m2_max": 0, "color": "lightgray", "alpha": 0.1}
    ]
    
    # 按时间顺序遍历M2数据，识别区域变化
    current_zone = None
    zone_start_date = None
    
    for i, row in monthly_df.iterrows():
        m2_value = row['M2_同比增长率']
        date = row['日期']
        
        # 确定当前M2值属于哪个区域
        zone = None
        for z in zones:
            if z["m2_min"] <= m2_value < z["m2_max"]:
                zone = z
                break
        
        # 如果是第一个点或者区域发生变化
        if current_zone != zone:
            # 如果之前有区域，先绘制它
            if current_zone is not None and zone_start_date is not None:
                ax1.axvspan(zone_start_date, date, 
                           color=current_zone["color"], alpha=current_zone["alpha"], 
                           label=current_zone["name"], zorder=0)
            
            # 开始新区域
            current_zone = zone
            zone_start_date = date
    
    # 绘制最后一个区域
    if current_zone is not None and zone_start_date is not None:
        ax1.axvspan(zone_start_date, monthly_df['日期'].iloc[-1], 
                   color=current_zone["color"], alpha=current_zone["alpha"], 
                   label=current_zone["name"], zorder=0)
    
    # 添加图例（只显示区域）- 合并到主图例中
    handles, labels = ax1.get_legend_handles_labels()
    if handles:
        # 过滤出区域图例
        zone_handles = []
        zone_labels = []
        zone_names = [z["name"] for z in zones]
        for handle, label in zip(handles, labels):
            if label in zone_names:
                zone_handles.append(handle)
                zone_labels.append(label)
        
        # 存储区域图例，稍后与数据线图例合并
        return zone_handles, zone_labels

def _add_investment_zones_advanced(ax1, ax2, monthly_df):
    """
    为高级图表添加竖向投资区域划分
    """
    # 定义区域阈值（基于M2同比增长率）- 按照投资周期顺序：建仓-加仓-减仓-清仓-观望
    zones = [
        {"name": "建仓期", "m2_min": 12, "m2_max": float('inf'), "color": "lightcoral", "alpha": 0.2},
        {"name": "加仓期", "m2_min": 8, "m2_max": 12, "color": "lightpink", "alpha": 0.15},
        {"name": "减仓期", "m2_min": 4, "m2_max": 8, "color": "lightgreen", "alpha": 0.15},
        {"name": "清仓期", "m2_min": 0, "m2_max": 4, "color": "lightblue", "alpha": 0.2},
        {"name": "观望期", "m2_min": float('-inf'), "m2_max": 0, "color": "lightgray", "alpha": 0.1}
    ]
    
    # 按时间顺序遍历M2数据，识别区域变化
    current_zone = None
    zone_start_date = None
    
    for i, row in monthly_df.iterrows():
        m2_value = row['M2_同比增长率']
        date = row['日期']
        
        # 确定当前M2值属于哪个区域
        zone = None
        for z in zones:
            if z["m2_min"] <= m2_value < z["m2_max"]:
                zone = z
                break
        
        # 如果是第一个点或者区域发生变化
        if current_zone != zone:
            # 如果之前有区域，先绘制它
            if current_zone is not None and zone_start_date is not None:
                ax1.axvspan(zone_start_date, date, 
                           color=current_zone["color"], alpha=current_zone["alpha"], 
                           label=current_zone["name"], zorder=0)
                ax2.axvspan(zone_start_date, date, 
                           color=current_zone["color"], alpha=current_zone["alpha"], 
                           zorder=0)
            
            # 开始新区域
            current_zone = zone
            zone_start_date = date
    
    # 绘制最后一个区域
    if current_zone is not None and zone_start_date is not None:
        ax1.axvspan(zone_start_date, monthly_df['日期'].iloc[-1], 
                   color=current_zone["color"], alpha=current_zone["alpha"], 
                   label=current_zone["name"], zorder=0)
        ax2.axvspan(zone_start_date, monthly_df['日期'].iloc[-1], 
                   color=current_zone["color"], alpha=current_zone["alpha"], 
                   zorder=0)
    
    # 为上方图表添加图例
    handles, labels = ax1.get_legend_handles_labels()
    if handles:
        # 过滤出区域图例
        zone_handles = []
        zone_labels = []
        zone_names = [z["name"] for z in zones]
        for handle, label in zip(handles, labels):
            if label in zone_names:
                zone_handles.append(handle)
                zone_labels.append(label)
        
        if zone_handles:
            ax1.legend(zone_handles, zone_labels, loc='upper left', fontsize=10, 
                      title='投资区域', title_fontsize=12, framealpha=0.9)

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("="*70)
print("恒生指数与M2货币供应量对比分析")
print("="*70)

# 1. 读取最终合并数据
print("正在读取最终合并数据...")
try:
    # 读取每日数据sheet
    daily_df = pd.read_excel('最终合并数据.xlsx', sheet_name='每日数据')
    daily_df['日期'] = pd.to_datetime(daily_df['日期'])
    
    print(f"✓ 每日数据: {len(daily_df)} 条记录")
    print(f"  时间范围: {daily_df['日期'].min().strftime('%Y-%m-%d')} 至 {daily_df['日期'].max().strftime('%Y-%m-%d')}")
    
    # 从每日数据中提取恒生指数月末数据
    print("正在提取恒生指数月末数据...")
    daily_df['年月'] = daily_df['日期'].dt.to_period('M')
    hsi_monthly = daily_df.groupby('年月').agg({
        '恒生指数': 'last',
        '日期': 'last'
    }).reset_index(drop=True)
    
    # 从每日数据中提取月度数据
    print("正在处理月度数据...")
    
    # 从每日数据中提取M2同比增长率（每月一个值）
    m2_monthly = daily_df.groupby('年月').agg({
        'M2_同比增长率': 'first'  # 每月第一个值（因为每日数据中同月的数据相同）
    }).reset_index()
    
    # 合并恒生指数月末数据和M2月度数据
    hsi_monthly['年月'] = hsi_monthly['日期'].dt.to_period('M')
    
    monthly_df = pd.merge(hsi_monthly, m2_monthly[['年月', 'M2_同比增长率']], on='年月', how='inner')
    
    # 计算M2环比增长率（从同比增长率反推）
    print("正在计算M2环比增长率...")
    monthly_df['M2_环比增长率'] = monthly_df['M2_同比增长率'].diff()  # 简化计算
    
    monthly_df.drop('年月', axis=1, inplace=True)
    
    print(f"✓ 月度数据: {len(monthly_df)} 条记录")
    print(f"  时间范围: {monthly_df['日期'].min().strftime('%Y-%m')} 至 {monthly_df['日期'].max().strftime('%Y-%m')}")
    
except Exception as e:
    print(f"❌ 读取失败: {e}")
    print("请确保 '最终合并数据.xlsx' 文件存在")
    exit()

# 2. 检查数据列
print("\n正在检查数据列...")
print("每日数据列:", daily_df.columns.tolist())
print("每日数据前3行:")
print(daily_df.head(3))
print("\n月度数据列:", monthly_df.columns.tolist())
print("月度数据前3行:")
print(monthly_df.head(3))

# 3. 计算M2环比增长率（如果不存在）
if 'M2_环比增长率' not in monthly_df.columns:
    print("\n正在计算M2环比增长率...")
    # 需要重新读取原始货币数据来计算环比
    try:
        money_raw = pd.read_excel('T020201.xlsx', sheet_name='T2.2.1 (new series)', header=None)
        
        # 提取M2原始数据
        data_rows = []
        for i in range(13, len(money_raw)):
            row = money_raw.iloc[i]
            year = row.iloc[0]
            month_en = row.iloc[1]
            
            if pd.notna(year) and str(year).replace('.0', '').isdigit():
                year = int(float(year))
                if month_en in ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']:
                    m2 = pd.to_numeric(row.iloc[10], errors='coerce')
                    if pd.notna(m2):
                        month_map = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6,
                                   'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
                        date = pd.to_datetime(f"{year}-{month_map[month_en]}-01")
                        data_rows.append({'日期': date, 'M2_原始': m2})
        
        money_df = pd.DataFrame(data_rows)
        money_df.sort_values('日期', inplace=True)
        
        # 计算环比增长率
        money_df['M2_环比增长率'] = money_df['M2_原始'].pct_change(1) * 100
        
        # 合并到月度数据
        money_df['年月'] = money_df['日期'].dt.to_period('M')
        monthly_df['年月'] = monthly_df['日期'].dt.to_period('M')
        
        monthly_df = pd.merge(monthly_df, money_df[['年月', 'M2_环比增长率']], on='年月', how='left')
        monthly_df.drop('年月', axis=1, inplace=True)
        
        print(f"✓ M2环比增长率计算完成")
        
    except Exception as e:
        print(f"❌ 计算M2环比增长率失败: {e}")
        # 如果没有环比数据，就只用同比数据
        pass

# 4. 保存处理后的数据到新的Excel文件
print("\n正在保存处理后的数据...")
with pd.ExcelWriter('恒生指数与M2数据_最终版.xlsx', engine='openpyxl') as writer:
    daily_df.to_excel(writer, sheet_name='恒生指数_日数据', index=False)
    monthly_df.to_excel(writer, sheet_name='M2_月度数据', index=False)

print("✓ 数据已保存到: 恒生指数与M2数据_最终版.xlsx")
print("  - 恒生指数_日数据: 恒生指数每日数据")
print("  - M2_月度数据: M2同比增长率和环比增长率月度数据")

# 5. 计算相关性
print("\n" + "="*70)
print("相关性分析")
print("="*70)

# 使用月度数据计算相关性
if 'M2_同比增长率' in monthly_df.columns:
    corr_m2_yoy = monthly_df['M2_同比增长率'].corr(monthly_df['恒生指数'])
    print(f"M2同比增长率 与 恒生指数相关系数: {corr_m2_yoy:.4f}")

if 'M2_环比增长率' in monthly_df.columns:
    corr_m2_mom = monthly_df['M2_环比增长率'].corr(monthly_df['恒生指数'])
    print(f"M2环比增长率 与 恒生指数相关系数: {corr_m2_mom:.4f}")

# 6. 绘制图表：恒生指数（日）与M2同比、环比（月）在同一图上
print("\n正在生成对比图表...")

fig, ax1 = plt.subplots(figsize=(20, 12))

# 左轴：恒生指数（每日数据）
ax1.set_xlabel('日期', fontsize=14)
ax1.set_ylabel('恒生指数', color='red', fontsize=14, fontweight='bold')
line1 = ax1.plot(daily_df['日期'], daily_df['恒生指数'], 
                 color='red', linewidth=2, label='恒生指数(日)', alpha=0.8)
ax1.tick_params(axis='y', labelcolor='red', labelsize=12)
ax1.grid(True, alpha=0.6, linestyle='--', linewidth=0.8)
ax1.grid(True, alpha=0.4, linestyle=':', linewidth=0.5, which='minor')

# 右轴：M2同比增长率和环比增长率（月度数据）
ax2 = ax1.twinx()
ax2.set_ylabel('M2增长率(%)', fontsize=14, fontweight='bold')

lines_to_plot = []
labels_to_plot = []

# M2同比增长率
if 'M2_同比增长率' in monthly_df.columns:
    line2 = ax2.plot(monthly_df['日期'], monthly_df['M2_同比增长率'], 
                     color='blue', linewidth=2, label='M2同比增长率(月)', alpha=0.7, marker='o', markersize=4)
    lines_to_plot.extend(line2)
    labels_to_plot.append('M2同比增长率(月)')

# M2环比增长率
if 'M2_环比增长率' in monthly_df.columns:
    line3 = ax2.plot(monthly_df['日期'], monthly_df['M2_环比增长率'], 
                     color='green', linewidth=2, label='M2环比增长率(月)', alpha=0.7, marker='s', markersize=4)
    lines_to_plot.extend(line3)
    labels_to_plot.append('M2环比增长率(月)')

ax2.tick_params(axis='y', labelsize=12)
ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

# 设置横坐标刻度为年
ax1.xaxis.set_major_locator(mdates.YearLocator())
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax1.xaxis.set_minor_locator(mdates.MonthLocator())  # 每个月都有次要刻度

# 合并图例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=12, framealpha=0.9)

plt.title('恒生指数(日)与M2货币供应量增长率(月)对比分析', 
          fontsize=18, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('恒生指数与M2对比图.png', dpi=300, bbox_inches='tight')
print("✓ 图表已保存到: 恒生指数与M2对比图.png")

# 添加投资区域划分
print("正在添加投资区域划分...")
zone_handles, zone_labels = _add_investment_zones(ax1, ax2, monthly_df)

# 合并所有图例并放在上方
print("正在合并图例...")
all_handles = []
all_labels = []
all_handles.extend(lines_to_plot)
all_labels.extend(labels_to_plot)
all_handles.extend(zone_handles)
all_labels.extend(zone_labels)

# 将图例放在图表上方，水平排列
ax1.legend(all_handles, all_labels, loc='upper center', bbox_to_anchor=(0.5, 1.15), 
          ncol=len(all_handles), fontsize=10, framealpha=0.9)

# 显示交互式图表
print("\n📊 正在显示交互式图表...")
print("操作说明:")
print("- 鼠标滚轮：缩放")
print("- 鼠标左键拖拽：平移")
print("- 右键：重置视图")
print("- 工具栏：更多工具（放大镜、十字线等）")
print("- 关闭窗口继续...")

plt.show()  # 显示交互式窗口

# 8. 绘制图表：只有恒生指数和M2同比增长率
print("\n正在生成恒生指数与M2同比增长率对比图...")

fig2, ax1_simple = plt.subplots(figsize=(20, 12))

# 左轴：恒生指数（每日数据）
ax1_simple.set_xlabel('日期', fontsize=14)
ax1_simple.set_ylabel('恒生指数', color='red', fontsize=14, fontweight='bold')
line1_simple = ax1_simple.plot(daily_df['日期'], daily_df['恒生指数'], 
                               color='red', linewidth=2, label='恒生指数(日)', alpha=0.8)
ax1_simple.tick_params(axis='y', labelcolor='red', labelsize=12)
ax1_simple.grid(True, alpha=0.6, linestyle='--', linewidth=0.8)
ax1_simple.grid(True, alpha=0.4, linestyle=':', linewidth=0.5, which='minor')

# 右轴：M2同比增长率（月度数据）
ax2_simple = ax1_simple.twinx()
ax2_simple.set_ylabel('M2同比增长率(%)', fontsize=14, fontweight='bold')

# 使用平滑折线图显示月度数据（带节点符号）
line2_simple = ax2_simple.plot(monthly_df['日期'], monthly_df['M2_同比增长率'], 
                               color='blue', linewidth=2, label='M2同比增长率(月)', alpha=0.7, marker='o', markersize=4)
ax2_simple.tick_params(axis='y', labelsize=12)
ax2_simple.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

# 设置横坐标刻度为年
ax1_simple.xaxis.set_major_locator(mdates.YearLocator())
ax1_simple.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax1_simple.xaxis.set_minor_locator(mdates.MonthLocator())  # 每个月都有次要刻度

# 合并图例
lines1_simple, labels1_simple = ax1_simple.get_legend_handles_labels()
lines2_simple, labels2_simple = ax2_simple.get_legend_handles_labels()
ax1_simple.legend(lines1_simple + lines2_simple, labels1_simple + labels2_simple, 
                  loc='upper left', fontsize=12, framealpha=0.9)

plt.title('恒生指数(日)与M2货币供应量同比增长率(月)对比分析', 
          fontsize=18, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('恒生指数与M2同比增长率对比图.png', dpi=300, bbox_inches='tight')
print("✓ 图表已保存到: 恒生指数与M2同比增长率对比图.png")

# 添加投资区域划分
print("正在添加投资区域划分...")
zone_handles_simple, zone_labels_simple = _add_investment_zones(ax1_simple, ax2_simple, monthly_df)

# 合并所有图例并放在上方
print("正在合并图例...")
all_handles_simple = []
all_labels_simple = []
lines1_simple, labels1_simple = ax1_simple.get_legend_handles_labels()
lines2_simple, labels2_simple = ax2_simple.get_legend_handles_labels()
all_handles_simple.extend(lines1_simple)
all_labels_simple.extend(labels1_simple)
all_handles_simple.extend(lines2_simple)
all_labels_simple.extend(labels2_simple)
all_handles_simple.extend(zone_handles_simple)
all_labels_simple.extend(zone_labels_simple)

# 将图例放在图表上方，水平排列
ax1_simple.legend(all_handles_simple, all_labels_simple, loc='upper center', bbox_to_anchor=(0.5, 1.15), 
                 ncol=len(all_handles_simple), fontsize=10, framealpha=0.9)

# 显示第二个交互式图表
print("\n📊 正在显示第二个交互式图表...")
print("操作说明:")
print("- 鼠标滚轮：缩放")
print("- 鼠标左键拖拽：平移")
print("- 右键：重置视图")
print("- 工具栏：更多工具（放大镜、十字线等）")
print("- 关闭窗口继续...")

plt.show()  # 显示第二个交互式窗口

# 9. 创建高级交互式图表（带更多功能）
print("\n" + "="*70)
print("生成高级交互式图表...")
print("="*70)

# 创建一个更高级的交互式图表
fig3, (ax1_advanced, ax2_advanced) = plt.subplots(2, 1, figsize=(20, 16))

# 上图：恒生指数
ax1_advanced.plot(daily_df['日期'], daily_df['恒生指数'], 
                  color='red', linewidth=2, label='恒生指数(日)', alpha=0.8)
ax1_advanced.set_ylabel('恒生指数', color='red', fontsize=14, fontweight='bold')
ax1_advanced.tick_params(axis='y', labelcolor='red', labelsize=12)
ax1_advanced.grid(True, alpha=0.6, linestyle='--', linewidth=0.8)
ax1_advanced.grid(True, alpha=0.4, linestyle=':', linewidth=0.5, which='minor')
ax1_advanced.legend(fontsize=12)
ax1_advanced.set_title('恒生指数走势', fontsize=16, fontweight='bold')

# 下图：M2同比增长率
ax2_advanced.plot(monthly_df['日期'], monthly_df['M2_同比增长率'], 
                  color='blue', linewidth=2, label='M2同比增长率(月)', alpha=0.7, marker='o', markersize=4)
ax2_advanced.set_ylabel('M2同比增长率(%)', color='blue', fontsize=14, fontweight='bold')
ax2_advanced.tick_params(axis='y', labelcolor='blue', labelsize=12)
ax2_advanced.grid(True, alpha=0.6, linestyle='--', linewidth=0.8)
ax2_advanced.grid(True, alpha=0.4, linestyle=':', linewidth=0.5, which='minor')
ax2_advanced.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax2_advanced.legend(fontsize=12)
ax2_advanced.set_title('M2货币供应量同比增长率走势', fontsize=16, fontweight='bold')
ax2_advanced.set_xlabel('日期', fontsize=14)

# 设置横坐标刻度
for ax in [ax1_advanced, ax2_advanced]:
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())

# 为高级图表添加投资区域划分
print("正在为高级图表添加投资区域划分...")
_add_investment_zones_advanced(ax1_advanced, ax2_advanced, monthly_df)

plt.suptitle('恒生指数与M2货币供应量综合分析（高级交互版）', 
             fontsize=20, fontweight='bold', y=0.98)
plt.tight_layout()

# 保存高级图表
plt.savefig('恒生指数与M2综合分析_高级版.png', dpi=300, bbox_inches='tight')
print("✓ 高级图表已保存到: 恒生指数与M2综合分析_高级版.png")

# 显示高级交互式图表
print("\n📊 正在显示高级交互式图表...")
print("功能说明:")
print("- 鼠标滚轮：缩放")
print("- 鼠标左键拖拽：平移")
print("- 右键：重置视图")
print("- 工具栏功能:")
print("  * 放大镜：区域放大")
print("  * 十字线：精确定位数值")
print("  * 平移：移动视图")
print("  * 缩放：整体缩放")
print("  * 配置：调整子图间距")
print("  * 保存：保存当前视图")
print("- 关闭窗口完成...")

plt.show()

# 7. 显示统计信息
print("\n" + "="*70)
print("数据统计")
print("="*70)
print(f"恒生指数数据: {len(daily_df)} 条记录")
print(f"M2月度数据: {len(monthly_df)} 条记录")
print(f"恒生指数范围: {daily_df['恒生指数'].min():,.0f} 至 {daily_df['恒生指数'].max():,.0f}")

if 'M2_同比增长率' in monthly_df.columns:
    print(f"M2同比增长率范围: {monthly_df['M2_同比增长率'].min():.2f}% 至 {monthly_df['M2_同比增长率'].max():.2f}%")

if 'M2_环比增长率' in monthly_df.columns:
    print(f"M2环比增长率范围: {monthly_df['M2_环比增长率'].min():.2f}% 至 {monthly_df['M2_环比增长率'].max():.2f}%")

print("\n" + "="*70)
print("分析结论")
print("="*70)

# M2同比增长率分析
if 'M2_同比增长率' in monthly_df.columns:
    if abs(corr_m2_yoy) > 0.7:
        m2_yoy_strength = "强相关"
    elif abs(corr_m2_yoy) > 0.4:
        m2_yoy_strength = "中等相关"
    else:
        m2_yoy_strength = "弱相关"
    
    m2_yoy_direction = "正" if corr_m2_yoy > 0 else "负"
    print(f"• M2同比增长率与恒生指数呈{m2_yoy_direction}{m2_yoy_strength} (r={corr_m2_yoy:.4f})")

# M2环比增长率分析
if 'M2_环比增长率' in monthly_df.columns:
    if abs(corr_m2_mom) > 0.7:
        m2_mom_strength = "强相关"
    elif abs(corr_m2_mom) > 0.4:
        m2_mom_strength = "中等相关"
    else:
        m2_mom_strength = "弱相关"
    
    m2_mom_direction = "正" if corr_m2_mom > 0 else "负"
    print(f"• M2环比增长率与恒生指数呈{m2_mom_direction}{m2_mom_strength} (r={corr_m2_mom:.4f})")

print("\n✓ 分析完成！")
print("="*70)