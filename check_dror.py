# check_dror.py

import os
import sys
import gspread

# קובץ ה-credentials נוצר באופן זמני ע"י ה-Action מתוך ה-Secret
CREDENTIALS_FILE = 'gsheets_credentials.json' 
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')
SHEET_NAME = 'Sheet1' # **שנה לשם הגיליון המדויק**
CHILD_NAME = os.environ.get('CHILD_NAME') # **משתנה חדש: קבלת שם הילד**

def check_dror_status():
    """ מתחבר לגיליון, בודק תא A2, ונכשל אם הוא ריק. """
    try:
        # התחברות ל-Google Sheets באמצעות חשבון השירות
        gc = gspread.service_account(filename=CREDENTIALS_FILE)
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.worksheet(SHEET_NAME) 

        # קריאת כל הנתונים 
        data = worksheet.get_all_values()
        
        # --- לוגיקת בדיקה: בודקת האם תא A2 ריק (שורה 2, עמודה 1) ---
        
        # ודא שהגיליון גדול מספיק
        if len(data) < 2 or len(data[1]) < 1:
             print("הגיליון קטן מדי לבדיקה או ריק.")
             return 

        # גישה לערך בתא A2 (אינדקסים 1, 0)
        target_cell_value = data[1][0] 

        # בדיקה: אם התא ריק (לאחר הסרת רווחים) - זה חסר!
        if not target_cell_value.strip(): 
            print(f"🚨 התראה: חסר נתון משמעותי עבור {CHILD_NAME} בגיליון.")
            # ** יציאה עם קוד 1 מכשילה את ה-Action ומפעילה את ה-Telegram **
            sys.exit(1) 
        
        # -----------------------------------------------------------
        
        print(f"✅ הכל תקין עבור {CHILD_NAME}. לא נדרשת התראה.")
        
    except Exception as e:
        # כשל טכני בגישה לגיליון - נרצה התראה גם על זה
        print(f"⚠️ אירעה שגיאה בגישה לגיליון: {e}")
        sys.exit(1) 

if __name__ == "__main__":
    check_dror_status()
