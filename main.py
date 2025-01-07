from flask import Flask, jsonify
from flask_restful import Api, Resource
import os
import hashlib
import time
import threading
import requests


app = Flask(__name__)
api = Api(app)

# تنظیم آدرس API که هش ها به آن ارسال می شوند
API_ENDPOINT = "YOUR_API_ENDPOINT_HERE"  # جایگزین کنید



# متغیر برای نگهداری هش قبلی برای جلوگیری از ارسال های تکراری
previous_hash = None
monitoring_enabled = False


def calculate_directory_hash(directory):
    """محاسبه هش دقیق از تمام فایل ها و پوشه های داخل یک دایرکتوری."""
    hasher = hashlib.sha256()
    all_items = []
    for root, dirs, files in os.walk(directory):
        # اطمینان از ترتیب یکسان برای هش پایدار
        dirs.sort()
        files.sort()

        # اضافه کردن اطلاعات پوشه به هش
        for dirname in dirs:
            full_dirname = os.path.join(root, dirname)
            all_items.append(f"DIR:{full_dirname}")

        # اضافه کردن اطلاعات فایل به هش
        for filename in files:
            full_filename = os.path.join(root, filename)
            try:
                with open(full_filename, 'rb') as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        hasher.update(chunk)
                all_items.append(f"FILE:{full_filename}:{os.path.getsize(full_filename)}:{os.path.getmtime(full_filename)}")
            except Exception as e:
                print(f"خطا در خواندن فایل {full_filename}: {e}")

            # هش کردن لیست مرتب شده از نام فایل ها و پوشه ها
        for item in sorted(all_items):
            hasher.update(item.encode('utf-8'))

        return hasher.hexdigest()



def send_hash_to_api(directory, api_url):
    """ارسال هش دایرکتوری به API مشخص شده."""
    global previous_hash
    current_hash = calculate_directory_hash(directory)

    if current_hash != previous_hash:
        try:
            payload = {'directory_hash': current_hash, 'directory_path': directory}
            response = requests.post(api_url, json=payload)
            response.raise_for_status()  # ایجاد خطا برای کدهای وضعیت ناموفق (4xx یا 5xx)
            print(f"هش دایرکتوری {directory} با موفقیت ارسال شد. کد وضعیت: {response.status_code}")
            previous_hash = current_hash
        except requests.exceptions.RequestException as e:
            print(f"خطا در ارسال هش به API: {e}")
    else:
        print(f"هش دایرکتوری {directory} تغییری نکرده است.")