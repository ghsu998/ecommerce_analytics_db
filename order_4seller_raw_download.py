from playwright.sync_api import sync_playwright

SELLER_URL = "https://www.4seller.com/login.html"
USERNAME = "gary@taigers.com"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, devtools=True)  # 啟動瀏覽器並開啟 DevTools
    context = browser.new_context()
    page = context.new_page()

    print("🌐 開啟 4Seller 登入頁面...")
    page.goto(SELLER_URL)

    try:
        # ✅ 使用 XPath 定位 Email 輸入框（相對路徑）
        email_xpath = '//input[@class="el-input__inner" and @type="text"]'
        
        # ✅ 等待 Email 欄位出現
        page.wait_for_selector(email_xpath, timeout=10000)
        
        # ✅ 輸入 Email
        page.fill(email_xpath, USERNAME)
        
        print("✅ 成功輸入 Email！")

    except Exception as e:
        print(f"❌ 錯誤: {e}")

    # **讓瀏覽器保持開啟，手動檢查 Email 欄位是否填寫成功**
    input("🔍 瀏覽器已開啟，請檢查 Email 欄位是否填寫正確後按 Enter 退出...")
    
    browser.close()