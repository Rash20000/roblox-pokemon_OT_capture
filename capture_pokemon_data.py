import csv
import os
import shutil
from datetime import datetime
from typing import Tuple, Dict, Union, List

import keyboard
import pyscreenshot
import pytesseract
import winsound

# Check if in debug mode
debug: Union[None, str] = os.getenv('debug')

# Set the path to Tesseract OCR executable. Check readme.md if you encounter issues with Tesseract.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Constants for sound notifications. Customize as needed.
NEW_OT_SOUND: Tuple[int, int] = (500, 100)
DUPLICATE_OT_SOUND: Tuple[int, int] = (2500, 1000)

# Constants for screenshot saving
SAVE_SCREENSHOTS: bool = True if debug or input(
    "Save screenshots?\n\t-yes\n\t-no\n").strip().lower() == 'yes' else False
SCREENSHOT_DIRECTORY: str = "./screenshots"
_MY_RES_H: int = 1080
_MY_RES_W: int = 1920

# Load old data from the last run
LOAD_OLD_DATA: bool = False if debug or input(
    "Load Old File Data?\n\t-yes\n\t-no\n").strip().lower() == 'yes' else False
CSV_FILE_PATH: str = 'All_OT_Pokemons.csv'

CAPTURE_HOT_KEY: str = '`' if debug else input("Enter hotkey to use to capture data from screen\n")

# Regions of interest for information extraction
FIELDS_CAPTURED: Dict[str, Tuple[int, int, int, int]] = {
    'Pokemon Name': (583, 113, 985, 207),
    'Ability': (691, 787, 933, 831),
    'OT': (1059, 675, 1389, 726),
    'Trainer ID': (1052, 730, 1378, 780)
}
FIELDNAMES: List[str] = list(FIELDS_CAPTURED.keys())

encountered_ids: set[str] = set()

def get_my_urls()->str:
    return """\t* Discord - rash2000 (455620017531256834)
\t* Linkedin - https://www.linkedin.com/in/rashil-dudhara/
\t* Roblox - https://www.roblox.com/users/98349498/profile"""


def initialize_csv() -> None:
    # Create screenshot directory if it doesn't exist
    if not os.path.isdir(SCREENSHOT_DIRECTORY):
        os.mkdir(SCREENSHOT_DIRECTORY)

    # Create CSV file if it doesn't exist
    if not os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, 'w', newline='') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            csv_writer.writeheader()
        print(f"CSV file {CSV_FILE_PATH} created.")
    else:
        if LOAD_OLD_DATA:
            print("Script has run before. Loading old OT IDs.")
            with open(input("Enter the name from last run").strip(), newline='') as csvfile:
                csv_reader: csv.DictReader = csv.DictReader(csvfile)
                row: Dict[str, str]
                for row in csv_reader:
                    encountered_ids.add(row['Trainer ID'])
            timestamp_file: str = f"""{datetime.now().strftime('%Y%m%d%H%M%S')}_Pokemons.csv"""
            os.rename(CSV_FILE_PATH, timestamp_file)
            print(f"Old file renamed as {timestamp_file}")


def extract_info(image: pyscreenshot.Image, screen_width: int, screen_height: int) -> Dict[str, str]:
    extracted_info: Dict[str, str] = {}
    poke_info: Dict[str, Tuple[str, pyscreenshot.Image]] = {'Pokemon Name': ('', None), 'Ability': ('', None),
                                                            'OT': ('', None),
                                                            'Trainer ID': ('', None)}

    for field, coordinates in FIELDS_CAPTURED.items():
        left, top, right, bottom = coordinates

        # Convert coordinates based on screen resolution
        left = left * (screen_width // _MY_RES_W)
        top = top * (screen_height // _MY_RES_H)
        right = right * (screen_width // _MY_RES_W)
        bottom = bottom * (screen_height // _MY_RES_H)

        region_image: pyscreenshot.Image = image.crop((left, top, right, bottom))

        text: str = pytesseract.pytesseract.image_to_string(region_image).replace(':', '').strip()
        extracted_info[field] = text
        poke_info[field] = text, region_image

    if SAVE_SCREENSHOTS:
        timestamp: str = datetime.now().strftime('%Y%m%d%H%M%S')
        image.save(
            f"{SCREENSHOT_DIRECTORY}/{poke_info['Pokemon Name'][0]}_{poke_info['Trainer ID'][0]}_{timestamp}.png")
        for field, (text, image) in poke_info.items():
            region_image_path: str = f"{SCREENSHOT_DIRECTORY}/" \
                                     f"{poke_info['OT'][0]}_{poke_info['Trainer ID'][0]}_{field}_{timestamp}.png"
            image.save(region_image_path)

    return extracted_info


def capture_and_extract() -> None:
    # Take a screenshot
    screenshot: pyscreenshot.Image = pyscreenshot.grab()
    screen_width: int
    screen_height: int
    screen_width, screen_height = screenshot.size

    # Extract information from the screenshot
    extracted_data: Dict[str, str] = extract_info(screenshot, screen_width, screen_height)

    # Print the extracted information
    for key, value in extracted_data.items():
        print(f"{key}: {value}")

    # Append the information to the CSV file
    with open(CSV_FILE_PATH, 'a', newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        csv_writer.writerow(extracted_data)

    # Sound notification
    if extracted_data['Trainer ID'] in encountered_ids:
        winsound.Beep(*DUPLICATE_OT_SOUND)
        print(f"{extracted_data['Pokemon Name']} is a duplicate OT for ID {extracted_data['Trainer ID']}")
    else:
        encountered_ids.add(extracted_data['Trainer ID'])
        winsound.Beep(*NEW_OT_SOUND)
    print()


# Register the hotkey for capturing and extracting
keyboard.add_hotkey(CAPTURE_HOT_KEY, capture_and_extract)
# Set up CSV file and load old OT IDs if needed
initialize_csv()
print(f"Program is now running. Enter your hotkey - {CAPTURE_HOT_KEY} to start capture")

# Keep the script running
keyboard.wait("esc")  # You can replace "esc" with any key to exit the script

if not SAVE_SCREENSHOTS:
    shutil.rmtree(SCREENSHOT_DIRECTORY)  # Clean up

print("User pressed 'ESC'. Exiting Program\n\n")
print("Thank you for trying out this script. Hopefully this met your expectations.")
print("I work as a full time software developer and enjoy playing pbb for fun and to escape the reality.")
print("If you had a positive or a negative experience, please please please reach out to me and let me know.")
print(get_my_urls())