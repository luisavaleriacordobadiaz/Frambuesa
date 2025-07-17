from grovepi import *
from grove_rgb_lcd import *
from time import sleep
from math import isnan
import pymysql

# Configuración del sensor DHT
dht_sensor_port = 7
dht_sensor_type = 0 # DHT11
setRGB(0, 255, 0)

# Conexión a la base de datos MariaDB local
try:
	conn=pymysql.connect(
		host="localhost",
		user="cilantropo",
		password="1234", # Déjalo vacío si no tiene contraseña
		database="LECTURAS"
	)
	cursor = conn.cursor()
except Exception as e:
	print("❌ Error al conectar con la base de datos:", e)
	exit(1)

# Bucle principal
try:
	while True:
		try:
			temp_hum = dht(dht_sensor_port, dht_sensor_type)
			if isinstance(temp_hum, list) and len(temp_hum) == 2:
				temp, hum = temp_hum

				if isnan(temp) or isnan(hum):
					print("⚠️ Lectura inválida: NaN")
					setText_norefresh("Esperado...")
				else:
					print("Temp = {} °C\tHumedad = {} %".format(temp, hum))

					setText_norefresh("Temp: {:.1f}C\nHumidity: {:.1f}%".format(temp, hum))

					sql = "INSERT INTO DATOS_RP (temperatura, humedad) VALUES (%s, %s)"
					try:
						cursor.execute(sql, (temp, hum))
						conn.commit()
					except Exception as e:
						print("❌ Error al guardar en la BD:", e)
			else:
				print("⚠️ Lectura corrupta del sensor")
				setText_norefresh("Sensor con error")

		except (IOError, TypeError) as e:
			print("⚠️ Error del sensor:", e)
			setText("Lectura\ninvalida")
			sleep(2)

		except KeyboardInterrupt:
			print("🛑 Programa interrumpido por el usuario.")
			setText("Detenido\npor usuario")
			break

		sleep(5)

finally:
	try:
		cursor.close()
	except:
		pass

	try:
		conn.close()
	except:
		pass
