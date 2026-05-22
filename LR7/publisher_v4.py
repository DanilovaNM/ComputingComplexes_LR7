import csv  # для построчного чтения сгенерированного файла
import time
import paho.mqtt.client as mqtt # библиотека для работы с протоколом MQTT

# Настройки MQTT
BROKER = "broker.emqx.io"  # адрес публичного тестового брокера
PORT = 1883     # стандартный порт MQTT без TLS-шифрования
TOPIC = "lab7/variant4/aperiodic"   # топик для передачи данных сигнала
LWT_TOPIC = "lab7/variant4/status"  # топик для сообщений о статусе подключения
CSV_FILE = "signal_v4.csv"  # путь к файлу с отсчётами
DELAY = 0.01  # задержка между сообщениями (с)

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:    # успех соединения с брокером
        print("[Publisher] Подключено к брокеру")
    else:
        print(f"[Publisher] Ошибка подключения: {reason_code}")

def on_disconnect(client, userdata, flags, reason_code, properties):
    print("[Publisher] Соединение разорвано")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="pub_v4_01")
# client_id должен быть уникальным на брокере, иначе второе подключение "выбросит" первое.
client.on_connect = on_connect  # привязывает локальные функции
client.on_disconnect = on_disconnect

client.connect(BROKER, PORT, keepalive=60)
client.loop_start()
time.sleep(1)  # ожидание установки соединения

print(f"[Publisher] Чтение {CSV_FILE} и отправка в топик {TOPIC}...")
with open(CSV_FILE, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # пропускаем заголовок
    for row in reader:
        msg = f"{row[0]},{row[1]}"
        info = client.publish(TOPIC, msg, qos=1)
        info.wait_for_publish() # подтверждение ухода сообщения
        print(f"  -> Отправлено: {msg}")
        time.sleep(DELAY)

    # Публикация финального статуса с retain=True (сохранение у брокера)
    client.publish(LWT_TOPIC, payload="Publisher finished", qos=1, retain=True)
    print("[+] Все данные отправлены.")
    
    client.loop_stop()
    client.disconnect()