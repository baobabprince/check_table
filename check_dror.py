# check_dror.py (מעודכן עבור מבנה RTL)

import os
import sys
import gspread

# --- הגדרות ---
CREDENTIALS_FILE = 'gsheets_credentials.json'
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
CHILD_NAME = os.environ.get('CHILD_NAME')

# רשימת הסטטוסים שמפעילים התראה (כשל)
STATUSES_TO_ALERT_ON = ['❌️', '🟰', '‼️'] 
# --- סוף הגדרות ---

# אינדקסים בהנחה שיש 6 עמודות סך הכל (0-5)
NAME_COLUMN_INDEX = 5 # העמודה האחרונה מימין מכילה את השמות
LAST_SUPPLY_INDEX = 4 # העמודה של 'טיטולים' (הכי רחוק מהשמות)

def check_child_supplies_status():
    """ מתחבר לגיליון, מאתר את שורת הילד במבנה RTL, ובודק את הסטטוסים. """
    try:
        # 1. התחברות וגישה לגיליון הראשון (אינדקס 0)
        gc = gspread.service_account(filename=CREDENTIALS_FILE)
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.get_worksheet(0) 

        # 2. קריאת כל הנתונים
        data = worksheet.get_all_values()
        
        if not data:
            print("הגיליון ריק.")
            return

        headers = data[0] # השורה הראשונה מכילה את שמות הציוד
        
        # 3. מציאת שורת הילד (השם נמצא בעמודה 5 - NAME_COLUMN_INDEX)
        child_row = None
        for row in data:
            # ודא שהשורה קיימת ושיש בה מספיק עמודות
            if len(row) > NAME_COLUMN_INDEX and row[NAME_COLUMN_INDEX].strip() == CHILD_NAME:
                child_row = row
                break
        
        if not child_row:
            print(f"⚠️ אזהרה: השם '{CHILD_NAME}' לא נמצא בעמודה הנכונה בגיליון.")
            sys.exit(1)

        # 4. בדיקת סטטוסים (עובר על העמודות של הציוד מ-0 עד 4)
        missing_items = []
        
        # עוברים על העמודות משמאל לימין (אינדקס 0 עד LAST_SUPPLY_INDEX)
        for i in range(LAST_SUPPLY_INDEX + 1): # כולל את LAST_SUPPLY_INDEX (אינדקס 4)
            if i >= len(headers) or i >= len(child_row):
                 # הגנה מפני שורות לא שלמות
                 continue

            item_name = headers[i].strip()
            item_status = child_row[i].strip()
            
            # בדיקת סטטוס מול רשימת האזהרה
            if item_status in STATUSES_TO_ALERT_ON:
                missing_items.append(f"{item_name} ({item_status})")
        
        # 5. סיכום והחלטה
        if missing_items:
            alert_message = f"🚨 חסר ציוד קריטי עבור {CHILD_NAME}:\n"
            alert_message += "\n".join(missing_items)
            
            print(alert_message)
            sys.exit(1) 
        
        # 6. הצלחה
        print(f"✅ הכל תקין עבור {CHILD_NAME}. לא נדרשת התראה.")
        
    except Exception as e:
        print(f"⚠️ שגיאה כללית: {e}")
        sys.exit(1) 

if __name__ == "__main__":
    check_child_supplies_status()
