import paho.mqtt.client as mqtt
import mysql.connector
from datetime import datetime
import json

# ========== KONFIGURASI MQTT ==========
MQTT_BROKER = "localhost"
MQTT_PORT = 9001
MQTT_USER = "AdminMQTT"
MQTT_PASS = "123"

TOPIC_TEMP = "sensor1/temp"
TOPIC_HUMID = "sensor1/humidity"
TOPIC_PRESSURE = "sensor1/pressure"
TOPIC_ALTITUDE = "sensor1/altitude"

# ========== KONFIGURASI MySQL ==========
DB_HOST = "localhost"
DB_USER = "root"           # Ganti dengan username MySQL-mu
DB_PASS = "Family1927/"  # Ganti dengan password MySQL-mu
DB_NAME = "mqtt_sensor"

# Variable untuk menyimpan data sementara
sensor_data = {
    'temperature': None,
    'humidity': None,
    'pressure': None,
    'altitude': None
}

# ========== KONEKSI MySQL ==========
def connect_mysql():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        print("✅ Connected to MySQL Database")
        return connection
    except mysql.connector.Error as err:
        print(f"❌ MySQL Error: {err}")
        return None

# ========== SIMPAN DATA KE MySQL ==========
def save_to_mysql(temp, humid, press, alt):
    conn = connect_mysql()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO sensor_data (temperature, humidity, pressure, altitude) 
                VALUES (%s, %s, %s, %s)
            """
            values = (temp, humid, press, alt)
            cursor.execute(query, values)
            conn.commit()
            print(f"💾 Data saved: Temp={temp}°C, Humidity={humid}%, Pressure={press}hPa, Altitude={alt}m")
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"❌ Error saving data: {err}")

# ========== CALLBACK MQTT ==========
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker")
        client.subscribe(TOPIC_TEMP)
        client.subscribe(TOPIC_HUMID)
        client.subscribe(TOPIC_PRESSURE)
        client.subscribe(TOPIC_ALTITUDE)
        print(f"📥 Subscribed to all sensor topics")
    else:
        print(f"❌ Connection failed with code {rc}")

def on_message(client, userdata, msg):
    global sensor_data
    
    topic = msg.topic
    payload = msg.payload.decode()
    
    try:
        value = float(payload)
        
        # Update data sesuai topik
        if topic == TOPIC_TEMP:
            sensor_data['temperature'] = value
            print(f"🌡️  Temperature: {value}°C")
        elif topic == TOPIC_HUMID:
            sensor_data['humidity'] = value
            print(f"💧 Humidity: {value}%")
        elif topic == TOPIC_PRESSURE:
            sensor_data['pressure'] = value
            print(f"🌀 Pressure: {value} hPa")
        elif topic == TOPIC_ALTITUDE:
            sensor_data['altitude'] = value
            print(f"⛰️  Altitude: {value} m")
        
        # Jika semua data sudah lengkap, simpan ke MySQL
        if all(v is not None for v in sensor_data.values()):
            save_to_mysql(
                sensor_data['temperature'],
                sensor_data['humidity'],
                sensor_data['pressure'],
                sensor_data['altitude']
            )
            # Reset data setelah disimpan
            sensor_data = {
                'temperature': None,
                'humidity': None,
                'pressure': None,
                'altitude': None
            }
            print("=" * 60)
    
    except ValueError:
        print(f"⚠️  Invalid data from {topic}: {payload}")

# ========== MAIN ==========
def main():
    # Buat MQTT Client
    client = mqtt.Client(transport="websockets")
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_connect = on_connect
    client.on_message = on_message
    
    print("🔄 Connecting to MQTT Broker...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    # Start loop
    print("🚀 MQTT to MySQL Bridge is running...")
    print("Press Ctrl+C to stop")
    client.loop_forever()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⛔ Stopped by user")