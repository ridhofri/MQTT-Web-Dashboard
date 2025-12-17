// ============================
// MQTT + MySQL Server
// ============================

const mqtt = require("mqtt");
const mysql = require("mysql2");

// --- Konfigurasi MQTT Broker ---
const mqttBroker = "localhost"; // Ganti sesuai broker-mu
const topicTemp = "sensor1/temp";
const topicHumidity = "sensor1/humidity";

// --- Koneksi ke MQTT Broker ---
const client = mqtt.connect(mqttBroker);

client.on("connect", () => {
  console.log("✅ Terhubung ke MQTT broker!");
  client.subscribe([topicTemp, topicHumidity], (err) => {
    if (!err) {
      console.log(`📡 Berlangganan pada topic: ${topicTemp} & ${topicHumidity}`);
    } else {
      console.error("❌ Gagal berlangganan topic:", err);
    }
  });
});

// --- Koneksi ke MySQL ---
const db = mysql.createConnection({
  host: "localhost",
  user: "root",         // sesuaikan
  password: "Family1927/",         // sesuaikan
  database: "monitoring", // sesuaikan nama DB
});

db.connect((err) => {
  if (err) {
    console.error("❌ Gagal konek ke MySQL:", err);
  } else {
    console.log("✅ Terhubung ke database MySQL!");
  }
});

// --- Variabel penyimpanan sementara ---
let latestTemp = null;
let latestHumidity = null;

// --- Fungsi untuk menyimpan data ke database ---
function insertData(temp, humidity) {
  const sql = "INSERT INTO sensor_data (temperature, humidity) VALUES (?, ?)";
  db.query(sql, [temp, humidity], (err, result) => {
    if (err) {
      console.error("❌ Error saat menyimpan ke database:", err);
    } else {
      console.log(`✅ Data tersimpan: Temp=${temp}°C | Humidity=${humidity}%`);
    }
  });
}

// --- Saat menerima pesan MQTT ---
client.on("message", (topic, message) => {
  const data = message.toString();

  if (topic === topicTemp) {
    latestTemp = parseFloat(data);
    console.log(`🌡️  Temperature updated: ${latestTemp} °C`);
  } else if (topic === topicHumidity) {
    latestHumidity = parseFloat(data);
    console.log(`💧 Humidity updated: ${latestHumidity} %`);
  }

  // Jika kedua data sudah tersedia, masukkan ke DB
  if (latestTemp !== null && latestHumidity !== null) {
    insertData(latestTemp, latestHumidity);
    latestTemp = null;
    latestHumidity = null;
  }
});
