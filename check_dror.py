# check_dror.py (מעודכן עם טיפול מיוחד לעמודת 'אחר')

import os
import sys
import gspread

# --- הגדרות ---
CREDENTIALS_FILE = 'gsheets_credentials.json'
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
CHILD_NAME = os.environ.get('CHILD_NAME')

# רשימת הסטטוסים שמפעילים התראה בפריטים הרגילים (בגדים, משחה וכו')
STATUSES_TO_ALERT_ON = ['❌️', '🟰', '‼️', ''] # כולל ריק כבעיה רגילה
# --- סוף הגדרות ---

NAME_COLUMN_INDEX = 6       # עמודה G
LAST_SUPPLY_INDEX = 5       # עמודה F (טיטולים)
FIRST_SUPPLY_INDEX = 1      # עמודה B (בגדים) - מתחילים מפריט זה בבדיקה הרגילה
OTHER_COLUMN_INDEX = 0      # עמודה A (אחר) - דורשת טיפול מיוחד


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

        headers = data[0] 
        
        # 3. מציאת שורת הילד (חיפוש רק בעמודה NAME_COLUMN_INDEX)
        child_row = None
        for row in data:
            if len(row) > NAME_COLUMN_INDEX and row[NAME_COLUMN_INDEX].strip() == CHILD_NAME:
                child_row = row
                break
        
        # 4. אם שם הילד לא נמצא
        if child_row is None:
            print(f"⚠️ אזהרה: השם '{CHILD_NAME}' לא נמצא בעמודה G (אינדקס {NAME_COLUMN_INDEX}).")
            sys.exit(1)
        
        # *** DEBUG ***
        print(f"DEBUG: Found '{CHILD_NAME}' at index {NAME_COLUMN_INDEX}.")
        print(f"DEBUG: Full data row: {child_row}")
        
        missing_items = []
        
        # 5. בדיקה מיוחדת לעמודת 'אחר' (אינדקס 0)
        # אם התא אינו ריק (יש שם טקסט/תוכן כלשהו), צריך התראה
        other_status = child_row[OTHER_COLUMN_INDEX].strip()
        other_name = headers[OTHER_COLUMN_INDEX].strip()
        
        if other_status != '':
            # התא אינו ריק. יש שם הערה, או תוכן כלשהו שמחייב בדיקה.
            missing_items.append(f"{other_name} ({other_status} - דורש בדיקה)")
            
        # 6. בדיקת סטטוסים רגילים: עוברים על העמודות 1 עד 5 (בגדים עד טיטולים)
        # הטווח הוא מ-FIRST_SUPPLY_INDEX (1) עד LAST_SUPPLY_INDEX (5)
        for i in range(FIRST_SUPPLY_INDEX, LAST_SUPPLY_INDEX + 1):
            if i >= len(headers) or i >= len(child_row):
                 continue

            item_name = headers[i].strip()
            item_status = child_row[i].strip()
            
            # בדיקת סטטוס מול רשימת האזהרה (כולל ריק)
            if item_status in STATUSES_TO_ALERT_ON: 
                missing_items.append(f"{item_name} ({item_status if item_status else 'ריק'})")
        
        # 7. סיכום והחלטה
        if missing_items:
            alert_message = f"🚨 חסר ציוד קריטי עבור {CHILD_NAME}:\n"
            alert_message += "\n".join(missing_items)
            
            print(alert_message)
            sys.exit(1) 
        
        # 8. הצלחה
        print(f"✅ הכל תקין עבור {CHILD_NAME}. לא נדרשת התראה.")
        
    except Exception as e:
        print(f"⚠️ שגיאה כללית: {e}")
        sys.exit(1) 

if __name__ == "__main__":
    check_child_supplies_status()
