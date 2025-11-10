# check_dror.py (מעודכן עבור עמודה G)

import os
import sys
import gspread

# --- הגדרות ---
CREDENTIALS_FILE = 'gsheets_credentials.json'
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
CHILD_NAME = os.environ.get('CHILD_NAME')

# רשימת הסטטוסים שמפעילים התראה (כשל)
STATUSES_TO_ALERT_ON = ['❌️', '🟰', '‼️', ''] # הוספנו תא ריק (ריק) ככישלון
# --- סוף הגדרות ---

# לפי ההערה, העמודה של השמות היא G. אם סופרים מ-A (0) עד F (5) ו-G (6).
NAME_COLUMN_INDEX = 6 
# עמודות הציוד הן האינדקסים משמאל לשם (0 עד 5)
LAST_SUPPLY_INDEX = 5 


def check_child_supplies_status():
    """ מתחבר לגיליון, מאתר את שורת הילד בעמודה G (אינדקס 6), ובודק את הסטטוסים משמאל. """
    try:
        # 1. התחברות וגישה לגיליון הראשון (אינדקס 0)
        gc = gspread.service_account(filename=CREDENTIALS_FILE)
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.get_worksheet(0) 

        # 2. קריאת כל הנתונים
        data = worksheet.get_all_values()
        
        if not data:
            print("הגיליון ריק.")
            sys.exit(1)

        headers = data[0] # השורה הראשונה מכילה את שמות הציוד
        
        # 3. מציאת שורת הילד (חיפוש רק בעמודה NAME_COLUMN_INDEX)
        child_row = None
        
        for row in data:
            # ודא שהשורה מכילה מספיק עמודות כדי להגיע ל-G
            if len(row) > NAME_COLUMN_INDEX and row[NAME_COLUMN_INDEX].strip() == CHILD_NAME:
                child_row = row
                break
        
        # 4. אם שם הילד לא נמצא בעמודה G, נכשל
        if child_row is None:
            print(f"⚠️ אזהרה: השם '{CHILD_NAME}' לא נמצא בעמודה G (אינדקס {NAME_COLUMN_INDEX}).")
            # הדפסת הכותרות והשורות לדוגמה כדי לגלות פערים
            print(f"DEBUG: Headers (Row 1): {headers}")
            print(f"DEBUG: First 3 data rows: {data[1:4]}")
            sys.exit(1)
        
        # *** DEBUG קריטי: נותן לנו את השורה הנכונה ***
        print(f"DEBUG: Found '{CHILD_NAME}' at index {NAME_COLUMN_INDEX}.")
        print(f"DEBUG: Full data row: {child_row}")
        
        # 5. בדיקת סטטוסים: עוברים על העמודות משמאל לשם (0 עד LAST_SUPPLY_INDEX=5)
        missing_items = []
        
        # טווח הבדיקה הוא מאינדקס 0 עד 5
        for i in range(LAST_SUPPLY_INDEX + 1): 
            if i >= len(headers) or i >= len(child_row):
                 continue

            item_name = headers[i].strip()
            item_status = child_row[i].strip()
            
            # בדיקת סטטוס מול רשימת האזהרה
            if item_status in STATUSES_TO_ALERT_ON: 
                # אם הסטטוס ריק או שהוא סטטוס אזהרה
                missing_items.append(f"{item_name} ({item_status if item_status else 'ריק'})")
        
        # 6. סיכום והחלטה
        if missing_items:
            alert_message = f"🚨 חסר ציוד קריטי עבור {CHILD_NAME}:\n"
            alert_message += "\n".join(missing_items)
            
            print(alert_message)
            sys.exit(1) 
        
        # 7. הצלחה
        print(f"✅ הכל תקין עבור {CHILD_NAME}. לא נדרשת התראה.")
        
    except Exception as e:
        print(f"⚠️ שגיאה כללית: {e}")
        sys.exit(1) 

if __name__ == "__main__":
    check_child_supplies_status()
