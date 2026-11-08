# Aspekte B2 — Native Runtime Preflight (v505-R141)

## نتیجه

- فایل دقیق **CURRENT v505-R141** از Library دریافت شد و SHA-256 آن تأیید شد. ZIP نیز بررسی CRC را گذراند.
- **۶ کنترل مستقل استاتیک/نحوی PASS**: ۷۰ فایل پوسته، ۸۲ هش Service Worker، ۶ سناریوی منفی و syntax فایل‌های حساس.
- **آزمون رسمی مرورگری اجرا شد، ولی پیش از بالا آمدن اپ متوقف شد**: `ERR_BLOCKED_BY_ADMINISTRATOR` هنگام بازکردن localhost در Chromium این محیط. هیچ یک از آزمون‌های native اجرا نشد. این نتیجه FAIL در محیط آزمون است، **نه اثبات خرابی اپ**.
- داده‌های شخصی، مرورها، کارت‌های واقعی یا نسخه برنامه تغییر نکردند. انتشار B2 همچنان `BLOCKED_NONIMPORT` است.

## اجرای امن در محیط مجاز

بستهٔ معتبر Flashcards Pro از Library (نام و SHA دقیق در JSON پیوست) را در یک پوشهٔ آزمایشی جدا استخراج کن. ابزارهای رسمی `03-Tests/native-flow.cjs` و `03-Tests/browser-common.cjs` داخل همان بسته هستند. این آزمون عمداً کارت‌های **ساختگی** می‌سازد و یک پروفایل جدید، نه پروفایل اصلی، استفاده می‌کند.

در Windows PowerShell با Node.js و Playwright از پیش نصب‌شده، پس از تعیین مسیرهای آزمایشی:

```powershell
$env:GFP_TEST_ROOT = 'C:\path\to\GFP505-WORDLINKS'
$env:GFP_TEST_WORK = 'C:\path\to\isolated-test-output'
$env:GFP_CHROMIUM = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
node "$env:GFP_TEST_ROOT\03-Tests\native-flow.cjs" b2-native-unique-test
```

هر بار یک برچسب جدید برای آزمون انتخاب کن؛ runner عمداً استفاده مجدد از پروفایل قبلی آزمون را رد می‌کند. برای انتشار، علاوه بر PASS واقعی این آزمون، شواهد معتبر و فقط‌خواندنی از شناسه‌های کارت‌های پذیرفته‌شده در پروفایل کاربر و QA مستقل آلمانی–فارسی لازم است.

**این گزارش تأیید Import یا SRS واقعی نیست.**
