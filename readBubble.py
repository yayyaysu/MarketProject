import requests
import json
from datetime import datetime
import time
import os

class BubbleAPI:
    def __init__(self, api_token=None):
        """
        初始化 Bubble API 客戶端
        
        參數:
            api_token (str): Bubble API 密鑰 (Private key)
        """
        # 修正 API 端點，確保使用正確的應用名稱
        self.base_url = "https://market-place-87091.bubbleapps.io/version-test/api/1.1"
        self.headers = {
            "Authorization": f"Bearer {api_token}" if api_token else None,
            "Content-Type": "application/json"
        }
        
        # 如果沒有提供 API token，則刪除 Authorization header
        if not api_token:
            del self.headers["Authorization"]
    
    def get_data(self, data_type, constraints=None, limit=100):
        """
        從 Bubble 數據庫獲取數據
        
        參數:
            data_type (str): 數據類型 (例如 'datatest')
            constraints (dict): 查詢條件
            limit (int): 返回結果數量限制
            
        返回:
            dict: API 響應
        """
        url = f"{self.base_url}/obj/{data_type}"
        
        params = {"limit": limit}
        
        if constraints:
            params["constraints"] = json.dumps(constraints)
            
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    def get_by_id(self, data_type, item_id):
        """
        通過 ID 獲取單條數據
        
        參數:
            data_type (str): 數據類型
            item_id (str): 數據項 ID
            
        返回:
            dict: API 響應
        """
        url = f"{self.base_url}/obj/{data_type}/{item_id}"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    def create_data(self, data_type, data):
        """
        創建新數據
        
        參數:
            data_type (str): 數據類型
            data (dict): 要創建的數據
            
        返回:
            dict: API 響應
        """
        url = f"{self.base_url}/obj/{data_type}"
        
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    def update_data(self, data_type, item_id, data):
        """
        更新數據
        
        參數:
            data_type (str): 數據類型
            item_id (str): 數據項 ID
            data (dict): 更新的數據
            
        返回:
            dict: API 響應
        """
        url = f"{self.base_url}/obj/{data_type}/{item_id}"
        response = requests.put(url, headers=self.headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
        if response.status_code in [200, 204]:
            return response.json() if response.content else True
        else:
            return None
    
    def delete_data(self, data_type, item_id):
        """
        刪除數據
        
        參數:
            data_type (str): 數據類型
            item_id (str): 數據項 ID
            
        返回:
            bool: 操作是否成功
        """
        url = f"{self.base_url}/obj/{data_type}/{item_id}"
        response = requests.delete(url, headers=self.headers)
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
        return response.status_code == 200 or response.status_code == 204

def test_bubble_api():
    api_token = os.getenv("BUBBLE_API_TOKEN")
    if not api_token:
        raise ValueError("未設置 BUBBLE_API_TOKEN 環境變數")
    
    # 初始化 API 客戶端
    bubble = BubbleAPI(api_token)
    
    # 測試創建 datatest 資料
    print("正在創建測試數據...")
    test_data = {
        "data": f"Test data created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }
    
    create_result = bubble.create_data("datatest", test_data)
    
    if create_result:
        record_id = create_result["id"]
        print(f"創建成功! ID: {record_id}")
        
        # 測試獲取數據
        print("\n正在獲取所有 datatest 數據...")
        all_data = bubble.get_data("datatest")
        if all_data:
            print(f"獲取到 {len(all_data['response']['results'])} 條記錄")
            for record in all_data['response']['results'][:5]:  # 只打印前5條記錄
                print(f"- ID: {record.get('_id')}, Data: {record.get('data', 'N/A')}")
            
        # 測試獲取單條數據
        print(f"\n正在獲取 ID 為 {record_id} 的數據...")
        single_data = bubble.get_by_id("datatest", record_id)
        if single_data:
            print(f"數據內容: {json.dumps(single_data, indent=2, ensure_ascii=False)}")
            
        # 測試更新數據
        print("\n正在更新數據...")
        update_data = {
            "data": f"Updated test data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        update_result = bubble.update_data("datatest", record_id, update_data)
        if update_result:
            print("更新成功!")
            print(f"更新後的數據: {json.dumps(update_result, indent=2, ensure_ascii=False)}")
            
        # 測試刪除數據
        print("\n是否要刪除測試數據? (y/n)")
        delete_choice = input().strip().lower()
        if delete_choice == 'y':
            delete_result = bubble.delete_data("datatest", record_id)
            if delete_result:
                print("刪除成功!")
            else:
                print("刪除失敗!")
        else:
            print(f"保留測試數據，ID: {record_id}")
    else:
        print("創建測試數據失敗!")
        print("嘗試直接獲取所有 datatest 數據...")
        all_data = bubble.get_data("datatest")
        if all_data and 'response' in all_data and 'results' in all_data['response']:
            print(f"獲取到 {len(all_data['response']['results'])} 條記錄")
            for record in all_data['response']['results'][:5]:  # 只打印前5條記錄
                print(f"- ID: {record.get('_id')}, Data: {record.get('data', 'N/A')}")
        else:
            print("無法獲取數據。請確認 API 端點和權限設置正確。")

# 新增一個功能，可以直接獲取所有數據而不需要創建測試資料
def get_all_datatest():
    api_token = os.getenv("BUBBLE_API_TOKEN")
    if not api_token:
        raise ValueError("未設置 BUBBLE_API_TOKEN 環境變數")
    
    # 初始化 API 客戶端
    bubble = BubbleAPI(api_token)
    
    # 獲取所有 datatest 數據
    print("正在獲取所有 datatest 數據...")
    all_data = bubble.get_data("datatest")
    if all_data and 'response' in all_data and 'results' in all_data['response']:
        print(f"獲取到 {len(all_data['response']['results'])} 條記錄")
        for record in all_data['response']['results']:
            print(f"- ID: {record.get('_id')}, Data: {record.get('data', 'N/A')}")
    else:
        print("無法獲取數據。請確認 API 端點和權限設置正確。")

if __name__ == "__main__":
    # 選擇要執行的功能
    print("請選擇要執行的功能：")
    print("1. 完整測試（創建、讀取、更新、刪除）")
    print("2. 只讀取所有數據")
    choice = input("請輸入選項（1 或 2）：").strip()
    
    if choice == "1":
        test_bubble_api()
    elif choice == "2":
        get_all_datatest()
    else:
        print("無效的選項。請輸入 1 或 2。")