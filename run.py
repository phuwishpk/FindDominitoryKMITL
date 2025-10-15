from app import create_app
from app.extensions import socketio # นำเข้า socketio

app = create_app()

if __name__ == "__main__":
    # **สำคัญมาก**: การกำหนด host และ port และใช้ socketio.run()
    # นี่คือวิธีที่ถูกต้องในการรัน Eventlet server พร้อม debug ใน local
    print("Running with Eventlet/SocketIO (Real-Time Mode)...")
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=True,
        # ต้องตั้งค่า allow_unsafe_werkzeug=True เพื่อให้ debug=True ใช้งานได้กับ Eventlet
        allow_unsafe_werkzeug=True 
    )

# **ไม่ต้องแก้ไขเพิ่มเติม**, Gunicorn หรือ Eventlet จะค้นหาตัวแปร `app` นี้โดยอัตโนมัติเมื่อใช้ Procfile
