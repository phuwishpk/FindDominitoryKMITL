from app import create_app
app = create_app()

if __name__ == "__main__":
    # ใช้ app.run() สำหรับ Local Development เท่านั้น
    app.run(debug=True)
# **ไม่ต้องแก้ไขเพิ่มเติม**, Gunicorn จะค้นหาตัวแปร `app` นี้โดยอัตโนมัติ
# กว่าจะดึงกลับมาได้โคตรยากเลยนะเนี่ย -*-