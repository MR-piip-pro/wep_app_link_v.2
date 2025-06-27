# Web Links Manager

## English

**Web Links Manager** is a simple web application for managing, searching, grouping, importing, and exporting your favorite links. Built with Python standard library only (no external dependencies), it provides a user-friendly interface to organize your web resources.

### Features
- Add, edit, and delete links with description, tags, and group.
- Search links by description, tags, or URL.
- Group links and filter by group.
- Import/export links as CSV or JSON.
- View statistics about your links.
- **No external dependencies** - uses only Python standard library.

### Installation & Usage on Linux

#### Prerequisites
- Python 3.8 or higher
- Terminal access

#### Step-by-Step Installation

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd web_links_manager
   ```

2. **Give execute permissions to the run script**
   ```bash
   chmod +x run_app.sh
   ```

3. **Run the application**
   
   **Method 1: Using the run script (Recommended)**
   ```bash
   ./run_app.sh
   ```
   
   **Method 2: Direct Python execution**
   ```bash
   python3 app.py
   ```

4. **Open your browser** and go to `http://localhost:8000`

#### Troubleshooting

**If you get "Permission denied" error:**
```bash
chmod +x run_app.sh
```

**If Python is not found:**
```bash
# Install Python 3
sudo apt update
sudo apt install python3 python3-pip
```

**If the port 8000 is already in use:**
Edit `app.py` and change the port number in the `run_server()` function.

### Technical Details
- **Web Server**: Python's built-in `http.server`
- **Database**: SQLite3 (built-in)
- **Form Processing**: Custom implementation using `urllib.parse`
- **No external packages required**

---

## العربية

**أداة إدارة الروابط** هي تطبيق ويب بسيط لإدارة، بحث، تجميع، استيراد وتصدير الروابط المفضلة لديك. مبني باستخدام مكتبات Python الأساسية فقط (بدون مكتبات خارجية) ويوفر واجهة سهلة لتنظيم الروابط.

### الميزات
- إضافة، تعديل، حذف الروابط مع وصف، كلمات مفتاحية، ومجموعة.
- البحث في الروابط حسب الوصف أو الكلمات المفتاحية أو الرابط.
- تجميع الروابط حسب المجموعة مع إمكانية التصفية.
- استيراد وتصدير الروابط بصيغة CSV أو JSON.
- عرض إحصائيات حول الروابط.
- **بدون مكتبات خارجية** - يستخدم مكتبات Python الأساسية فقط.

### طريقة التثبيت والتشغيل على Linux

#### المتطلبات الأساسية
- Python 3.8 أو أحدث
- وصول إلى الطرفية (Terminal)

#### خطوات التثبيت المفصلة

1. **استنساخ أو تحميل المشروع**
   ```bash
   git clone <رابط-المشروع>
   cd web_links_manager
   ```

2. **إعطاء صلاحيات التنفيذ لملف التشغيل**
   ```bash
   chmod +x run_app.sh
   ```

3. **تشغيل التطبيق**
   
   **الطريقة الأولى: استخدام سكريبت التشغيل (موصى بها)**
   ```bash
   ./run_app.sh
   ```
   
   **الطريقة الثانية: تشغيل Python مباشرة**
   ```bash
   python3 app.py
   ```

4. **افتح المتصفح** وادخل إلى `http://localhost:8000`

#### حل المشاكل الشائعة

**إذا ظهرت رسالة "Permission denied":**
```bash
chmod +x run_app.sh
```

**إذا لم يتم العثور على Python:**
```bash
# تثبيت Python 3
sudo apt update
sudo apt install python3 python3-pip
```

**إذا كان المنفذ 8000 مستخدماً:**
عدّل ملف `app.py` وغير رقم المنفذ في دالة `run_server()`.

### التفاصيل التقنية
- **خادم الويب**: `http.server` المدمج في Python
- **قاعدة البيانات**: SQLite3 (مدمج)
- **معالجة النماذج**: تنفيذ مخصص باستخدام `urllib.parse`
- **لا تحتاج مكتبات خارجية**

---

## Quick Start Commands (أوامر البدء السريع)

```bash
# Navigate to project directory
cd web_links_manager

# Give execute permissions
chmod +x run_app.sh

# Run the application
./run_app.sh

# Open browser and go to: http://localhost:8000
```

---

**ملاحظات مهمة:**
- قاعدة البيانات تحفظ تلقائياً في ملف `links.db`.
- جميع القوالب مدمجة في الكود.
- يمكنك استيراد وتصدير الروابط بسهولة من خلال الواجهة.
- التطبيق يعمل على المنفذ 8000.
- لإيقاف التطبيق، اضغط `Ctrl+C` في الطرفية. 