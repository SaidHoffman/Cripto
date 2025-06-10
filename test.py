import smtplib
import ssl
from email.mime.text import MIMEText

def test_smtp_connection():
    try:
        print("Probando conexión SMTP...")
        
        # Prueba 1: Puerto 587 con STARTTLS
        print("Probando puerto 587...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('saidsigala16@gmail.com', 'dxqa uiat ripe dbnu')
        print("✅ Conexión exitosa con puerto 587")
        # Enviar un correo de prueba
        msg = MIMEText("Este es un correo de prueba.")
        msg['Subject'] = 'Correo de prueba'
        msg['From'] = 'saidsigala16@gmail.com'
        msg['To'] = 'saidsigala14@gmail.com'  
        server.quit()
        
    except Exception as e:
        print(f"❌ Error con puerto 587: {e}")
        
        try:
            # Prueba 2: Puerto 465 con SSL
            print("Probando puerto 465...")
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context)
            server.login('saidsigala16@gmail.com', 'dxqa uiat ripe dbnu')
            print("✅ Conexión exitosa con puerto 465")
            server.quit()
            
        except Exception as e2:
            print(f"❌ Error con puerto 465: {e2}")
            print("El problema es de conectividad de red o credenciales")

test_smtp_connection()
