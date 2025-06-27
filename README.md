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

### Installation & Usage
1. **Clone the repository**
2. **No installation required** - uses only Python standard library
3. **Run the app**
   - On Linux:
     ```bash
     bash run_app.sh
     ```
   - On Windows:
     Double-click `run_app.bat` (if available) or run:
     ```bash
     python app.py
     ```
4. **Open your browser** and go to `http://localhost:8000`

### Technical Details
- **Web Server**: Python's built-in `http.server`
- **Database**: SQLite3 (built-in)
- **Form Processing**: CGI module (built-in)
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

### طريقة التثبيت والتشغيل
1. **استنساخ المشروع**
2. **لا حاجة للتثبيت** - يستخدم مكتبات Python الأساسية فقط
3. **تشغيل التطبيق**
   - على لينكس:
     ```bash
     bash run_app.sh
     ```
   - على ويندوز:
     شغّل `run_app.bat` (إن وجد) أو نفذ:
     ```bash
     python app.py
     ```
4. **افتح المتصفح** وادخل إلى `http://localhost:8000`

### التفاصيل التقنية
- **خادم الويب**: `http.server` المدمج في Python
- **قاعدة البيانات**: SQLite3 (مدمج)
- **معالجة النماذج**: وحدة CGI (مدمجة)
- **لا تحتاج مكتبات خارجية**

---

**ملاحظة:**
- قاعدة البيانات تحفظ تلقائياً في ملف `links.db`.
- جميع القوالب مدمجة في الكود.
- يمكنك استيراد وتصدير الروابط بسهولة من خلال الواجهة.
- التطبيق يعمل على المنفذ 8000 بدلاً من 5000. 