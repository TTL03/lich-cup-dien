import requests
import json
import re

# !!! DÁN URL BẠN VỪA SAO CHÉP TỪ TAB "HEADERS" VÀO ĐÂY !!!
API_URL = "https://ep1.adtrafficquality.google/getconfig/sodar?sv=200&tid=gpt&tv=m202508060101&st=env"

OUTPUT_FILE = "lich_cup_dien.json"

def get_and_process_data():
    try:
        print(f"Đang gọi tới API...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()

        # Dữ liệu API trả về có dạng `some_prefix({...});`
        # Chúng ta cần dùng biểu thức chính quy (regex) để trích xuất chuỗi JSON bên trong cặp ngoặc tròn
        raw_text = response.text
        match = re.search(r'\((.*)\)', raw_text, re.DOTALL)
        
        if not match:
            print("Không tìm thấy dữ liệu JSON hợp lệ trong phản hồi từ API.")
            return

        json_string = match.group(1)
        data = json.loads(json_string)

        # Dữ liệu thực sự nằm trong một cấu trúc lồng nhau của Google Sheets
        rows = data.get('table', {}).get('rows', [])
        
        outages = []
        # Bỏ qua hàng đầu tiên (là tiêu đề của bảng)
        for row in rows[1:]:
            cells = row.get('c', [])
            # Đảm bảo hàng có đủ 6 cột và có dữ liệu
            if len(cells) >= 6 and cells[1] is not None and cells[1].get('v') is not None:
                outage_data = {
                    "dien_luc": cells[0].get('v', 'N/A') if cells[0] else 'N/A',
                    "ngay": cells[1].get('v', 'N/A') if cells[1] else 'N/A',
                    "thoi_gian": cells[2].get('v', 'N/A') if cells[2] else 'N/A',
                    "khu_vuc": cells[3].get('v', 'N/A') if cells[3] else 'N/A',
                    "ly_do": cells[4].get('v', 'N/A') if cells[4] else 'N/A',
                    "trang_thai": cells[5].get('v', 'N/A') if cells[5] else 'N/A',
                }
                outages.append(outage_data)

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(outages, f, ensure_ascii=False, indent=2)

        print(f"Xử lý và lưu thành công {len(outages)} lịch cúp điện vào {OUTPUT_FILE}")

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

if __name__ == "__main__":
    get_and_process_data()
