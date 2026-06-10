from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import os

def fetch_sales_data(month):
    url = f"https://www.dongchedi.com/sales/sale-energy-{month}-x-x-x-x"
    
    # Edge浏览器配置（带界面模式）
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0")
    
    # 尝试设置Edge驱动路径
    edge_driver_path = r"D:\Program Files (x86)\Microsoft\Edge\Application\msedgedriver.exe"
    if not os.path.exists(edge_driver_path):
        edge_driver_path = None  # 让Selenium自动查找
    
    driver = None
    try:
        if edge_driver_path:
            driver = webdriver.Edge(executable_path=edge_driver_path, options=options)
        else:
            driver = webdriver.Edge(options=options)
        
        print(f"浏览器已启动，正在访问: {url}")
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
        time.sleep(10)
        
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
                        "sales": sales
                    })
                    print(f"第{rank}条: {brand.ljust(8)} {series.ljust(12)} {sales}")
            except Exception as e:
                print(f"解析第{index+1}条数据失败: {e}")
                continue
        
        return data
        
    except Exception as e:
        print(f"请求失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        # 保存页面源码以供分析
        if driver:
            with open(f"selenium_page_{month}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source[:20000])
            print(f"页面内容已保存到 selenium_page_{month}.html")
        return []
    finally:
        if driver:
            print("关闭浏览器...")
            driver.quit()

if __name__ == "__main__":
    month = "202604"
    print(f"正在爬取{month}月份的新能源汽车销售数据...")
    
    data = fetch_sales_data(month)
    
    if data:
        output_file = f"新能源汽车销售数据_{month}.csv"
        with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            # 表头：排名、品牌、车型、销量（移除能源类型）
            writer.writerow(["排名", "品牌", "车型", "销量"])
            
            for item in data:
                writer.writerow([
                    item["rank"],
                    item["brand"],
                    item["series"],
                    item["sales"]
                ])
        
        print(f"\n数据已成功保存到 {output_file}")
        print(f"共爬取了 {len(data)} 条记录")
    else:
        print("\n未获取到数据")
