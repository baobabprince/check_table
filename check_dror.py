# check_dror.py

import os
import sys
import gspread

# --- הגדרות ---
CREDENTIALS_FILE = 'gsheets_credentials.json'
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
SHEET_NAME = 'Sheet1' # **וודא שזהו שם הגיליון הנכון**
CHILD_NAME = os.environ.get('CHILD_NAME')

# רשימת הסטטוסים שמפעילים התראה (כשל)
STATUSES_TO_ALERT_ON = ['❌️', '🟰', '‼️'] 
# --- סוף הגדרות ---


def check_child_supplies_status():
    """ מתחבר לגיליון, מאתר את שורת הילד, ובודק את כל עמודות הציוד עבור סימני אזהרה. """
    try:
        # 1. התחברות ל-Google Sheets
        gc = gspread.service_account(filename=CREDENTIALS_FILE)
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.worksheet(SHEET_NAME) 

        # 2. קריאת כל הנתונים 
        data = worksheet.get_all_values()
        
        if not data:
            print("הגיליון ריק.")
            return

        # כותרות: השורה הראשונה
        headers = data[0]
        
        # 3. מציאת האינדקס של שורת הילד
        child_row = None
        for row in data:
            # נניח ששם הילד נמצא בעמודה הראשונה
            if row and row[0].strip() == CHILD_NAME:
                child_row = row
                break
        
        if not child_row:
            print(f"⚠️ אזהרה: השם '{CHILD_NAME}' לא נמצא בגיליון.")
            # במקרה של אי מציאת השם, נכשל טכנית
            sys.exit(1)

        # 4. מציאת טווח הבדיקה
        # נניח שהבדיקה מתחילה אחרי עמודת ה'שם' וה'נכון ל:'
        # נבדוק החל מהעמודה השנייה (אינדקס 2)
        
        missing_items = []
        # מתחילים מהעמודה השנייה או השלישית, תלוי איך הגיליון מוגדר.
        # בדוגמה ששלחת, הציוד מתחיל בעמודה השלישית (אחרי השם ושדה התאריך/נכון ל:)
        
        # נחפש את הציוד החל מהאינדקס 2 (כלומר, העמודה השלישית 'אחרתמ"ל')
        START_INDEX_FOR_SUPPLIES = 2 

        for i in range(START_INDEX_FOR_SUPPLIES, len(headers)):
            item_name = headers[i].strip()
            item_status = child_row[i].strip() if i < len(child_row) else ""
            
            # 5. בדיקת סטטוס מול רשימת האזהרה
            if item_status in STATUSES_TO_ALERT_ON:
                missing_items.append(f"{item_name} ({item_status})")
        
        # 6. סיכום והחלטה
        if missing_items:
            alert_message = f"🚨 חסר ציוד קריטי עבור {CHILD_NAME}:\n"
            alert_message += "\n".join(missing_items)
            
            print(alert_message)
            # ** יציאה עם קוד 1 מכשילה את ה-Action **
            sys.exit(1) 
        
        # 7. הצלחה
        print(f"✅ הכל תקין עבור {CHILD_NAME}. לא נדרשת התראה.")
        
    except Exception as e:
        print(f"⚠️ שגיאה כללית: {e}")
        sys.exit(1) 

if __name__ == "__main__":
    check_child_supplies_status()
