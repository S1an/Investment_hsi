import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from datetime import datetime, timedelta
import yfinance as yf

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("="*80)
print("恒生指数与M2货币供应量分析工作流")
print("="*80)
print("功能：下载数据 → 处理数据 → 生成图表 → 保存结果")
print("="*80)

class HSIM2Analyzer:
    def __init__(self):
        self.daily_df = None
        self.monthly_df = None
        self.money_df = None
        
    def step1_download_hsi(self, years=20):
        """
        步骤1：下载恒生指数数据
        """
        print("\n" + "="*60)
        print("步骤1：下载恒生指数数据")
        print("="*60)
        
        print(f"正在下载恒生指数近{years}年数据...")
        
        # 计算开始日期
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)
        
        print(f"时间范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
        
        try:
            # 下载恒生指数数据
            ticker = "^HSI"
            print(f"正在下载 {ticker} 数据...")
            
            data = yf.download(ticker, start=start_date, end=end_date)
            
            if data.empty:
                print("❌ 下载失败：未获取到数据")
                return False
            
            # 重置索引，将日期作为列
            data = data.reset_index()
            
            # 删除时区信息
            data['Date'] = data['Date'].dt.tz_localize(None)
            
            # 只保留需要的列
            data = data[['Date', 'Close']].copy()
            data.rename(columns={'Date': '日期', 'Close': '恒生指数'}, inplace=True)
            
            # 删除空值
            data = data.dropna()
            
            self.daily_df = data
            
            print(f"✓ 恒生指数下载成功！共 {len(data)} 条记录")
            print(f"  时间范围: {data['日期'].min().strftime('%Y-%m-%d')} 至 {data['日期'].max().strftime('%Y-%m-%d')}")
            print(f"  指数范围: {data['恒生指数'].min():.0f} 至 {data['恒生指数'].max():.0f}")
            
            return True
            
        except Exception as e:
            print(f"❌ 恒生指数下载失败: {e}")
            return False
    
    def step2_process_money_supply(self):
        """
        步骤2：处理货币供应量数据
        """
        print("\n" + "="*60)
        print("步骤2：处理货币供应量数据")
        print("="*60)
        
        print("正在读取货币供应量数据...")
        
        try:
            # 读取原始货币数据
            money_raw = pd.read_excel('T020201.xls', sheet_name='T2.2.1 (new series)', header=None)
            
            # 提取M2原始数据
            print("正在提取M2数据...")
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
            
            # 计算同比增长率和环比增长率
            print("正在计算M2增长率...")
            money_df['M2_同比增长率'] = money_df['M2_原始'].pct_change(12) * 100
            money_df['M2_环比增长率'] = money_df['M2_原始'].pct_change(1) * 100
            
            # 只保留2005年以后的数据
            money_df = money_df[money_df['日期'].dt.year >= 2005].copy()
            
            self.money_df = money_df
            
            print(f"✓ 货币供应量数据处理完成！共 {len(money_df)} 条记录")
            print(f"  时间范围: {money_df['日期'].min().strftime('%Y-%m')} 至 {money_df['日期'].max().strftime('%Y-%m')}")
            print(f"  M2同比增长率范围: {money_df['M2_同比增长率'].min():.2f}% 至 {money_df['M2_同比增长率'].max():.2f}%")
            
            return True
            
        except Exception as e:
            print(f"❌ 货币供应量数据处理失败: {e}")
            return False
    
    def step3_merge_data(self):
        """
        步骤3：合并数据
        """
        print("\n" + "="*60)
        print("步骤3：合并数据")
        print("="*60)
        
        if self.daily_df is None or self.money_df is None:
            print("❌ 数据未准备完成")
            return False
        
        try:
            # 从每日数据中提取恒生指数月末数据
            print("正在提取恒生指数月末数据...")
            daily_df_copy = self.daily_df.copy()
            daily_df_copy['年月'] = daily_df_copy['日期'].dt.to_period('M')
            hsi_monthly = daily_df_copy.groupby('年月').agg({
                '恒生指数': 'last',
                '日期': 'last'
            }).reset_index(drop=True)
            
            # 从每日数据中提取M2同比增长率（每月一个值）
            print("正在提取M2月度数据...")
            daily_df_copy['M2_同比增长率'] = daily_df_copy['日期'].apply(
                lambda x: self._get_m2_yoy_for_date(x)
            )
            m2_monthly = daily_df_copy.groupby('年月').agg({
                'M2_同比增长率': 'first'
            }).reset_index()
            
            # 合并月度数据
            hsi_monthly['年月'] = hsi_monthly['日期'].dt.to_period('M')
            monthly_df = pd.merge(hsi_monthly, m2_monthly[['年月', 'M2_同比增长率']], on='年月', how='inner')
            monthly_df.drop('年月', axis=1, inplace=True)
            
            self.monthly_df = monthly_df
            
            print(f"✓ 数据合并完成！")
            print(f"  每日数据: {len(self.daily_df)} 条记录")
            print(f"  月度数据: {len(monthly_df)} 条记录")
            print(f"  重叠时间范围: {monthly_df['日期'].min().strftime('%Y-%m')} 至 {monthly_df['日期'].max().strftime('%Y-%m')}")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据合并失败: {e}")
            return False
    
    def _get_m2_yoy_for_date(self, date):
        """
        获取指定日期对应的M2同比增长率
        """
        date_period = pd.to_datetime(date).to_period('M')
        matching_data = self.money_df[self.money_df['日期'].dt.to_period('M') == date_period]
        if len(matching_data) > 0:
            return matching_data['M2_同比增长率'].iloc[0]
        return None
    
    def step4_generate_charts(self):
        """
        步骤4：生成图表
        """
        print("\n" + "="*60)
        print("步骤4：生成图表")
        print("="*60)
        
        if self.daily_df is None or self.monthly_df is None:
            print("❌ 数据未准备完成")
            return False
        
        try:
            # 图表1：恒生指数与M2同比增长率对比
            print("正在生成恒生指数与M2同比增长率对比图...")
            
            fig, ax1 = plt.subplots(figsize=(20, 12))
            
            # 左轴：恒生指数（每日数据）
            ax1.set_xlabel('日期', fontsize=14)
            ax1.set_ylabel('恒生指数', color='red', fontsize=14, fontweight='bold')
            line1 = ax1.plot(self.daily_df['日期'], self.daily_df['恒生指数'], 
                           color='red', linewidth=2, label='恒生指数(日)', alpha=0.8)
            ax1.tick_params(axis='y', labelcolor='red', labelsize=12)
            ax1.grid(True, alpha=0.3, linestyle='--')
            
            # 右轴：M2同比增长率（月度数据）
            ax2 = ax1.twinx()
            ax2.set_ylabel('M2同比增长率(%)', fontsize=14, fontweight='bold')
            
            # 使用平滑折线图显示月度数据（带节点符号）
            line2 = ax2.plot(self.monthly_df['日期'], self.monthly_df['M2_同比增长率'], 
                           color='blue', linewidth=2, label='M2同比增长率(月)', alpha=0.7, marker='o', markersize=4)
            ax2.tick_params(axis='y', labelsize=12)
            ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
            
            # 设置横坐标刻度为年
            ax1.xaxis.set_major_locator(mdates.YearLocator())
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax1.xaxis.set_minor_locator(mdates.MonthLocator((1, 7)))
            
            # 合并图例
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=12, framealpha=0.9)
            
            plt.title('恒生指数(日)与M2货币供应量同比增长率(月)对比分析', 
                      fontsize=18, fontweight='bold', pad=20)
            plt.tight_layout()
            
            # 生成文件名（包含日期）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            chart_filename = f'恒生指数与M2同比增长率对比图_{timestamp}.png'
            plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
            print(f"✓ 图表已保存到: {chart_filename}")
            
            plt.close()
            
            return True
            
        except Exception as e:
            print(f"❌ 图表生成失败: {e}")
            return False
    
    def step5_save_data(self):
        """
        步骤5：保存数据
        """
        print("\n" + "="*60)
        print("步骤5：保存数据")
        print("="*60)
        
        if self.daily_df is None or self.monthly_df is None:
            print("❌ 数据未准备完成")
            return False
        
        try:
            # 生成文件名（包含日期）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 保存每日数据
            daily_filename = f'恒生指数每日数据_{timestamp}.xlsx'
            self.daily_df.to_excel(daily_filename, index=False, engine='openpyxl')
            print(f"✓ 每日数据已保存到: {daily_filename}")
            
            # 保存月度数据
            monthly_filename = f'M2月度数据_{timestamp}.xlsx'
            self.monthly_df.to_excel(monthly_filename, index=False, engine='openpyxl')
            print(f"✓ 月度数据已保存到: {monthly_filename}")
            
            # 保存合并数据
            with pd.ExcelWriter(f'恒生指数与M2分析数据_{timestamp}.xlsx', engine='openpyxl') as writer:
                self.daily_df.to_excel(writer, sheet_name='恒生指数_日数据', index=False)
                self.monthly_df.to_excel(writer, sheet_name='M2_月度数据', index=False)
            print(f"✓ 合并数据已保存到: 恒生指数与M2分析数据_{timestamp}.xlsx")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据保存失败: {e}")
            return False
    
    def step6_analysis_report(self):
        """
        步骤6：生成分析报告
        """
        print("\n" + "="*60)
        print("步骤6：生成分析报告")
        print("="*60)
        
        if self.monthly_df is None:
            print("❌ 数据未准备完成")
            return False
        
        try:
            # 计算相关性
            corr = self.monthly_df['M2_同比增长率'].corr(self.monthly_df['恒生指数'])
            
            # 生成报告
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_filename = f'恒生指数与M2分析报告_{timestamp}.txt'
            
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write("恒生指数与M2货币供应量分析报告\n")
                f.write("="*50 + "\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("数据统计:\n")
                f.write(f"- 恒生指数数据: {len(self.daily_df)} 条记录\n")
                f.write(f"- M2月度数据: {len(self.monthly_df)} 条记录\n")
                f.write(f"- 恒生指数范围: {self.daily_df['恒生指数'].min():.0f} 至 {self.daily_df['恒生指数'].max():.0f}\n")
                f.write(f"- M2同比增长率范围: {self.monthly_df['M2_同比增长率'].min():.2f}% 至 {self.monthly_df['M2_同比增长率'].max():.2f}%\n\n")
                
                f.write("相关性分析:\n")
                f.write(f"- M2同比增长率与恒生指数相关系数: {corr:.4f}\n")
                
                if abs(corr) > 0.7:
                    strength = "强相关"
                elif abs(corr) > 0.4:
                    strength = "中等相关"
                else:
                    strength = "弱相关"
                
                direction = "正" if corr > 0 else "负"
                f.write(f"- 相关性强弱: {direction}{strength}\n\n")
                
                f.write("分析结论:\n")
                if corr > 0:
                    f.write("- M2同比增长率与恒生指数呈正相关，流动性充裕时股市表现较好\n")
                else:
                    f.write("- M2同比增长率与恒生指数呈负相关，流动性收紧时股市可能承压\n")
                
                f.write("- 建议关注M2增长趋势变化，作为市场流动性指标\n")
                f.write("- M2增长持续下降时，需警惕市场顶部风险\n")
            
            print(f"✓ 分析报告已保存到: {report_filename}")
            
            # 打印关键信息
            print(f"\n📊 分析结果:")
            print(f"  M2同比增长率与恒生指数相关系数: {corr:.4f}")
            print(f"  相关性强弱: {direction}{strength}")
            
            return True
            
        except Exception as e:
            print(f"❌ 分析报告生成失败: {e}")
            return False
    
    def run_full_workflow(self, years=20):
        """
        运行完整工作流
        """
        print("🚀 开始运行完整分析工作流...")
        
        steps = [
            ("下载恒生指数数据", self.step1_download_hsi, years),
            ("处理货币供应量数据", self.step2_process_money_supply, None),
            ("合并数据", self.step3_merge_data, None),
            ("生成图表", self.step4_generate_charts, None),
            ("保存数据", self.step5_save_data, None),
            ("生成分析报告", self.step6_analysis_report, None)
        ]
        
        success_count = 0
        
        for step_name, step_func, arg in steps:
            try:
                if arg is not None:
                    success = step_func(arg)
                else:
                    success = step_func()
                
                if success:
                    success_count += 1
                    print(f"✅ {step_name} - 完成")
                else:
                    print(f"❌ {step_name} - 失败")
                    break
                    
            except Exception as e:
                print(f"❌ {step_name} - 异常: {e}")
                break
        
        print(f"\n🎉 工作流完成！成功步骤: {success_count}/{len(steps)}")
        
        if success_count == len(steps):
            print("✅ 所有步骤执行成功！")
        else:
            print("⚠️ 部分步骤执行失败，请检查错误信息")

def main():
    """
    主函数
    """
    analyzer = HSIM2Analyzer()
    
    # 运行完整工作流
    analyzer.run_full_workflow(years=20)
    
    print("\n" + "="*80)
    print("工作流执行完毕")
    print("="*80)

if __name__ == "__main__":
    main()
