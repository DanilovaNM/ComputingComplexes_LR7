import paho.mqtt.client as mqtt # клиентская библиотека MQTT
import matplotlib.pyplot as plt  # библиотека для визуализации данных
import time

BROKER = "broker.emqx.io"
PORT = 1883
# Wildcard: подписка на все вложенные топики lab7/variant4/*
TOPIC_WILDCARD = "lab7/variant4/#"
TOPIC_DATA = "lab7/v4/data"

# пустые списки для накопления координат графика
x_data, y_data = [], []

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"[Subscriber] Подключено. Подписка на {TOPIC_WILDCARD}")
        client.subscribe(TOPIC_WILDCARD, qos=1)
    else:
        print(f"[Subscriber] Ошибка подключения: {reason_code}")

def on_message(client, userdata, msg):
    # Фильтрация: обрабатываем только основной топик, игнорируем status
    if msg.topic == TOPIC_WILDCARD.replace("/#", "/aperiodic"):
        t_str, amp_str = msg.payload.decode().split(',')
        x_data.append(float(t_str))
        y_data.append(float(amp_str))

# Инициализация клиента paho-mqtt v2
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="sub_v4_01")
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, keepalive=60)
client.loop_start()

# Настройка интерактивного графика
plt.ion()
fig, ax = plt.subplots(figsize=(8, 5))
line, = ax.plot([], [], 'r-', linewidth=2, marker='o', markersize=3)
ax.set_xlabel('Время, с')
ax.set_ylabel('Амплитуда')
ax.set_title('Сигнал апериодического звена')
ax.grid(True, linestyle='--', alpha=0.6)
ax.set_xlim(0, 0.3)
ax.set_ylim(0, 6)

try:
    print("[Subscriber] Ожидание данных... Запустите publisher_v4.py в другом терминале.")
    while True:
        if x_data:
            # обновляет координаты линии
            line.set_data(x_data, y_data)
            # пересчитывает границы
            ax.relim()
            ax.autoscale_view()
            
            fig.canvas.draw()
            fig.canvas.flush_events()
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\n[Subscriber] Завершение работы по Ctrl+C")
finally:
    client.loop_stop()
    client.disconnect()
    plt.close(fig)
