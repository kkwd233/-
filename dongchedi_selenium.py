from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import os

def fetch_sales_data(month, driver):
    """使用已存在的driver爬取指定月份的数据"""
    url = f"https://www.dongchedi.com/sales/sale-energy-{month}-x-x-x-x"
    
    try:
        print(f"\n{'='*50}")
        print(f"正在访问: {url}")
        driver.get(url)
        
        # 等待页面加载（最多60秒）
        print("等待页面加载...")
        try:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except Exception as e:
            print(f"等待超时: {e}")
            print(f"当前URL: {driver.current_url}")
        
        # 检查是否被重定向到验证码页面
        if "captcha" in driver.current_url.lower() or "验证" in driver.title:
            print("检测到验证码页面，请手动完成验证")
            # 等待用户手动完成验证（最多5分钟）
            for i in range(300):
                if "captcha" not in driver.current_url.lower() and "验证" not in driver.title:
                    break
                time.sleep(1)
                if i % 30 == 0:
                    print(f"等待验证中... ({i}秒)")
        
        # 等待数据加载
        print("等待数据加载...")
        time.sleep(5)

        # 等待用户手动点击批发量按钮
        print("请在浏览器中手动点击批发量按钮...")
        print("等待5秒...")
        time.sleep(5)

        # 自动向下滚动页面以加载更多数据
        print("自动滚动页面...")
        scroll_pause_time = 2
        scroll_height = 1000
        
        # 滚动几次
        for i in range(12):
            # 向下滚动
            driver.execute_script(f"window.scrollBy(0, {scroll_height});")
            time.sleep(scroll_pause_time)
            print(f"  已滚动 {scroll_height * (i+1)} 像素")
        
        # 等待数据加载
        time.sleep(3)
        
        # 获取页面标题
        print(f"页面标题: {driver.title}")
        
        # 获取列表项 - 使用精确的选择器
        list_items = driver.find_elements(By.CSS_SELECTOR, "#__next ol li")
        print(f"找到 {len(list_items)} 条数据")
        
        # 如果没有找到，尝试其他选择器
        if len(list_items) == 0:
            list_items = driver.find_elements(By.CSS_SELECTOR, "ol li")
            print(f"使用备用选择器，找到 {len(list_items)} 条数据")
        
        data = []
        for index, item in enumerate(list_items):
            try:
                # 获取排名（从索引+1）
                rank = index + 1
                
                # 获取品牌 - 使用精确选择器
                brand = ""
                brand_element = item.find_element(By.CSS_SELECTOR, "div.tw-py-16.tw-pr-12 > div.tw-leading-28.tw-h-28.tw-truncate > span")
                if brand_element:
                    brand = brand_element.text.strip()
                
                # 获取车型 - 使用精确选择器
                series = ""
                series_element = item.find_element(By.CSS_SELECTOR, "div.tw-py-16.tw-pr-12 > div.tw-leading-28.tw-h-28.tw-truncate > a")
                if series_element:
                    series = series_element.text.strip()
                
                # 获取销量 - 使用精确选择器
                sales = ""
                sales_element = item.find_element(By.CSS_SELECTOR, "div.tw-py-16.tw-text-center > div > p")
                if sales_element:
                    sales_text = sales_element.text.strip()
                    # 只保留数字和逗号
                    sales = ''.join([c for c in sales_text if c.isdigit() or c == ','])
                
                # 过滤无效数据（必须同时有品牌和销量）
                if brand and sales:
                    data.append({
                        "rank": rank,
                        "brand": brand,
                        "series": series,
                        "sales": sales,
                        "month": month
                    })
                    if index < 5:  # 只打印前5条
                        print(f"第{rank}条: {brand.ljust(8)} {series.ljust(12)} {sales}")
            except Exception as e:
                # 静默处理错误，继续下一条
                continue
        
        print(f"成功提取 {len(data)} 条有效数据")
        return data
        
    except Exception as e:
        print(f"爬取{month}月份数据失败: {type(e).__name__}: {e}")
        return []

def generate_months(start_year, start_month, end_year, end_month):
    """生成月份列表"""
    months = []
    year, month = start_year, start_month
    while (year < end_year) or (year == end_year and month <= end_month):
        months.append(f"{year}{month:02d}")
        month += 1
        if month > 12:
            month = 1
            year += 1
    return months

def main():
    # 输出目录
    output_dir = r"D:\学习\A正在学的\商务数据分析\lunwen\data\yuedu_pifa"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    print(f"数据将保存到: {output_dir}")
    # 在此处修改时间！！！！
    # 在此处修改时间！！！！
    months = generate_months(2023, 1, 2026, 5)
    # 在此处修改时间！！！！
    # 在此处修改时间！！！！
    print(f"需要爬取的月份: {months}")
    print(f"共 {len(months)} 个月份")
    
    # 创建单个浏览器实例，重复使用
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0")
    
    # 尝试设置Edge驱动路径
    edge_driver_path = r"D:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe"
    if not os.path.exists(edge_driver_path):
        edge_driver_path = None
    
    driver = None
    all_data = []
    
    try:
        print("\n启动浏览器...")
        if edge_driver_path:
            driver = webdriver.Edge(executable_path=edge_driver_path, options=options)
        else:
            driver = webdriver.Edge(options=options)
        
        # 逐个爬取每个月份的数据
        for month in months:
            data = fetch_sales_data(month, driver)
            if data:
                all_data.extend(data)
                
                # 保存单月数据
                month_file = os.path.join(output_dir, f"新能源汽车销售数据_{month}.csv")
                with open(month_file, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["排名", "品牌", "车型", "销量"])
                    for item in data:
                        writer.writerow([
                            item["rank"],
                            item["brand"],
                            item["series"],
                            item["sales"]
                        ])
                print(f"✅ {month}月份数据已保存: {month_file}")
            else:
                print(f"❌ {month}月份数据爬取失败")
            
            # 每个月份之间等待3秒，避免请求过快
            time.sleep(3)
        
        # 保存合并数据
        if all_data:
            combined_file = os.path.join(output_dir, "新能源汽车销售数据_202401-202605.csv")
            with open(combined_file, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["年月", "排名", "品牌", "车型", "销量"])
                for item in all_data:
                    writer.writerow([
                        item["month"],
                        item["rank"],
                        item["brand"],
                        item["series"],
                        item["sales"]
                    ])
            print(f"\n{'='*50}")
            print(f"✅ 所有数据已合并保存: {combined_file}")
            print(f"📊 总计爬取 {len(all_data)} 条记录")
        
    except Exception as e:
        print(f"程序运行失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            print("\n关闭浏览器...")
            driver.quit()

if __name__ == "__main__":
    main()
