from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

RECEIVED_HASHES_FILE = "received_hashes.json"  # نام فایل ذخیره داده‌ها

def save_to_json_file(data, file_name):
    """ذخیره داده‌ها در فایل JSON."""
    if os.path.exists(file_name):
        # اگر فایل وجود دارد، داده‌های قبلی را بارگذاری کنید
        with open(file_name, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    # اضافه کردن داده جدید به لیست موجود
    existing_data.append(data)

    # ذخیره تمام داده‌ها در فایل JSON
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

@app.route('/receive_hash/', methods=['POST'])
def receive_hash():
    data = request.get_json()
    if data and 'hash_value' in data and 'directory_path' in data:
        hash_value = data['hash_value']
        directory_path = data['directory_path']
        received_data = {
            'hash_value': hash_value,
            'directory_path': directory_path,
            'received_at': datetime.now().isoformat()  # تاریخ و زمان دریافت
        }
        save_to_json_file(received_data, RECEIVED_HASHES_FILE)
        return jsonify({'message': 'هش با موفقیت دریافت شد.', 'received_data': received_data}), 201
    else:
        return jsonify({'error': 'فرمت درخواست نامعتبر است. باید شامل hash_value و directory_path باشد.'}), 400

@app.route('/hashes/', methods=['GET'])
def get_all_hashes():
    if os.path.exists(RECEIVED_HASHES_FILE):
        with open(RECEIVED_HASHES_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return jsonify(data)
    else:
        return jsonify({'message': 'هیچ هشی ذخیره نشده است.'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # پورت API دریافت کننده فلَسک
