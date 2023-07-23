import asyncio, sqlite3
from dotenv import load_dotenv, find_dotenv
from os import getenv
from config import url_external, url_internal, api_key, url_site
import requests, json, os
import bot
from datetime import datetime

load_dotenv(find_dotenv())


CHAT_ID = getenv("YOUR_CHAT_ID")
chat_id = CHAT_ID

current_directory = os.path.dirname(os.path.abspath(__file__))
database_filename = "user_number.db"
db_file_path = os.path.join(current_directory, database_filename)


class CallDataProcessor:
    def __init__(self, db_file_path, url_site):
        self.db_file_path = db_file_path
        self.url_site = url_site
        self.create_table()
        self.clients_to_send = []
        self.is_data_added = False

    def create_table(self):
        connection = sqlite3.connect(self.db_file_path)
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT UNIQUE,
                type TEXT,
                diversion TEXT,
                start TEXT
            )
        """
        )
        connection.commit()
        connection.close()

    def insert_client(self, client_data):
        client_number = client_data.get("client")
        client_type = client_data.get("type", "N/A")
        client_diversion = client_data.get("diversion", "N/A")
        start_time_str = client_data.get("start", "N/A")

        connection = sqlite3.connect(self.db_file_path)
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO clients (number, type, diversion, start) VALUES (?, ?, ?, ?)",
                (client_number, client_type, client_diversion, start_time_str),
            )
            connection.commit()
            print(f"Номер клиента {client_number} добавлен в базу данных.")
            self.is_data_added = True  # Устанавливаем флаг, что данные были добавлены
        except sqlite3.IntegrityError:
            pass
        connection.close()

        self.clients_to_send.append(
            {"client_number": client_number, "employee_number": client_diversion}
        )

    def send_post_requests(self):
        if self.is_data_added:  # Проверяем, были ли добавлены данные
            for client_data in self.clients_to_send:
                client_number = client_data["client_number"]
                employee_number = client_data["employee_number"]
                post_data = {"phone": client_number, "employee_number": employee_number}
                try:
                    response = requests.post(self.url_site, json=post_data)
                    if response.status_code == 200:
                        print(
                            f"POST request sent successfully for client: {client_number}."
                        )
                    else:
                        print(
                            f"Failed to send POST request for client: {client_number}. Status code: {response.status_code}"
                        )
                except requests.exceptions.RequestException as e:
                    print(
                        f"Error occurred while sending POST request for client: {client_number}. Error: {e}"
                    )
                except Exception as ex:
                    print(
                        f"Unknown error occurred while sending POST request for client: {client_number}. Error: {ex}"
                    )

            # Очищаем список после отправки всех POST-запросов
            self.clients_to_send.clear()

            # Сбрасываем флаг, так как данные были отправлены
            self.is_data_added = False

    def process_json_file(self):
        if os.path.exists(self.json_file_path):
            with open(self.json_file_path, "r") as file:
                json_data = json.load(file)

            for call in json_data:
                client_data = call.get("client")
                if client_data:
                    self.process_client_data(client_data)
        else:
            print(f"JSON file not found: {self.json_file_path}")


class Message_Json_Ex:
    def __init__(
        self, api_key="api_key", url_external="url_external", save_directory=None
    ):
        self.api_key = api_key
        self.url_external = url_external
        self.save_directory = save_directory or os.path.join(
            os.path.dirname(__file__), "json_files"
        )
        self.json_file = os.path.join(self.save_directory, "external_calls.json")

    def get_history(self):
        params = {"period": "this_week", "type": "all", "limit": 1}
        headers = {"X-API-KEY": self.api_key}

        res = requests.get(url=self.url_external, params=params, headers=headers)
        if res.status_code == 200:
            json_data = res.json()

            os.makedirs(self.save_directory, exist_ok=True)

            if not os.path.exists(self.json_file):
                with open(self.json_file, "w") as file:
                    json.dump(json_data, file)

            return json_data
        else:
            print("Failed to fetch external data. Status code:", res.status_code)
            print("Response content:", res.content)
            return None


class Message_Json_In:
    def __init__(
        self, api_key="api_key", url_internal="url_internal", save_directory=None
    ):
        self.api_key = api_key
        self.url_internal = url_internal
        self.save_directory = save_directory or os.path.join(
            os.path.dirname(__file__), "json_files"
        )
        self.json_file = os.path.join(self.save_directory, "internal_calls.json")

    def get_history(self):
        params = {"period": "this_week", "type": "all", "limit": 1}
        headers = {"X-API-KEY": self.api_key}

        res = requests.get(url=self.url_internal, params=params, headers=headers)
        print(res.status_code)
        if res.status_code == 200:
            json_data = res.json()

            os.makedirs(self.save_directory, exist_ok=True)

            if not os.path.exists(self.json_file):
                with open(self.json_file, "w") as file:
                    json.dump(json_data, file)

            return json_data
        else:
            print("Failed to fetch external data. Status code:", res.status_code)
            print("Response content:", res.content)
            return None


class Call_Info_Ex:
    info_call_ex = []

    def __init__(self, chat_id, save_directory=None):
        self.info_call_ex = self.load_data()
        self.chat_id = chat_id
        self.save_directory = save_directory or os.path.join(
            os.path.dirname(__file__), "json_files"
        )

    def load_data(self):
        file_path = os.path.join(
            os.path.dirname(__file__), "json_files", "external_calls.json"
        )
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                json_data = json.load(file)
            return json_data
        return []  # Return an empty list if the file doesn't exist

    def download_file(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            os.makedirs(self.save_directory, exist_ok=True)
            file_name = os.path.basename(url)
            file_path = os.path.join(self.save_directory, file_name)
            with open(file_path, "wb") as file:
                file.write(response.content)
            return file_path  # Return the file path if downloaded successfully
        else:
            print("Failed to download file. Status code:", response.status_code)
            return None

    async def check_and_send_message(self, new_data):
        for call in new_data:
            if call not in self.info_call_ex:
                self.info_call_ex.append(call)
                message = self.create_message(call)

                # Check if the 'record' field is present in the call data
                record_url = call.get("record")
                if record_url:
                    audio_file_path = self.download_file(record_url)
                else:
                    audio_file_path = None

                await bot.send_data_to_chat(message, audio_file_path)

    def create_message(self, call):
        message = "Внешний звонок\n"
        start_time_str = call.get("start")
        if start_time_str:
            start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%SZ")
            formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M")
            message += f"Время начала звонка: {formatted_start_time}\n"
        else:
            message += "Время начала звонка: Неизвестно\n"
        message += f"Ожидание: {call.get('wait', 'N/A')}\n"
        message += f"Продолжительность: {call.get('duration', 'N/A')}\n"
        message += f"Тип звонка: {call.get('type', 'N/A')}\n"
        message += f"Статус звонка: {call.get('status', 'N/A')}\n"
        message += f"Номер сотрудника: {call.get('diversion', 'N/A')}\n"
        message += f"Сотрудник: {call.get('user', 'N/A')}\n\n"
        message += f"Номер клиента: {call.get('client', 'N/A')}\n"
        return message

    def message_ex(self, message):
        self.bot.send_message(chat_id=self.chat_id, text=message)


class Call_Info_In:
    info_call_in = []

    def __init__(self, chat_id, save_directory=None):
        self.info_call_ex = self.load_data()
        self.chat_id = chat_id
        self.save_directory = save_directory or os.path.join(
            os.path.dirname(__file__), "json_files"
        )

    def load_data(self):
        file_path = os.path.join(
            os.path.dirname(__file__), "json_files", "internal_calls.json"
        )
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                json_data = json.load(file)
            return json_data
        return []  # Return an empty list if the file doesn't exist

    def download_file(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            os.makedirs(self.save_directory, exist_ok=True)
            file_name = os.path.basename(url)
            file_path = os.path.join(self.save_directory, file_name)
            with open(file_path, "wb") as file:
                file.write(response.content)
            return file_path  # Return the file path if downloaded successfully
        else:
            print("Failed to download file. Status code:", response.status_code)
            return None

    async def check_and_send_message(self, new_data):
        for call in new_data:
            if call not in self.info_call_ex:
                self.info_call_ex.append(call)
                message = self.create_message(call)

                # Check if the 'record' field is present in the call data
                record_url = call.get("record")
                if record_url:
                    audio_file_path = self.download_file(record_url)
                else:
                    audio_file_path = None

                await bot.send_data_to_chat(message, audio_file_path)

    def create_message(self, call):
        message = "Вннутренний звонок\n"
        start_time_str = call.get("start")
        if start_time_str:
            start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%SZ")
            formatted_start_time = start_time.strftime("%Y-%m-%d %H:%M")
            message += f"Время начала звонка: {formatted_start_time}\n"
        else:
            message += "Время начала звонка: Неизвестно\n"
        message += f"Ожидание: {call['wait']}\n"
        message += f"Продолжительность: {call.get('duration', 'N/A')}\n"
        message += f"Статус звонка: {call['status']}\n"
        message += f"От: {call.get('from_name', 'N/A')}\n"  # Используем 'N/A' по умолчанию, если ключ 'from_name' отсутствует
        message += f"Кому: {call.get('to_name', 'N/A')}\n"  # Используем 'N/A' по умолчанию, если ключ 'to_name' отсутствует

        return message

    def message_in(self, message):
        self.bot.send_message(chat_id=self.chat_id, text=message)


async def start_run():
    # Initialize the event loop
    loop = asyncio.get_event_loop()

    # Create instances of Call_Info_Ex and Call_Info_In with appropriate save_directory
    call_info_ex = Call_Info_Ex(
        chat_id, save_directory="your_external_save_directory_here"
    )
    call_info_in = Call_Info_In(
        chat_id, save_directory="your_internal_save_directory_here"
    )

    # Create instances of Message_Json_Ex and Message_Json_In with appropriate API keys and URLs
    get_ex = Message_Json_Ex(api_key, url_external)
    get_in = Message_Json_In(api_key, url_internal)

    db_file_path = os.path.join(
        os.path.dirname(__file__), "user_number.db"
    )  # Add this line to get the correct db_file_path

    # Pass the 'url_site' argument from config.py
    db_handler = CallDataProcessor(db_file_path, url_site)  # Передаем url_site здесь

    while True:
        external_data = get_ex.get_history()
        internal_data = get_in.get_history()

        if external_data:
            await call_info_ex.check_and_send_message(external_data)

        if internal_data:
            await call_info_in.check_and_send_message(internal_data)

        if external_data:
            for call in external_data:
                db_handler.insert_client(call)

        await asyncio.sleep(0.5)

        # Выполняем отправку POST-запросов только один раз после обработки всех внешних данных
        db_handler.send_post_requests()
