from flask import Flask, request, render_template, send_file
from PIL import Image
import os
import io

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def scale_and_compress(image, scale_percentage=None, width=None, height=None, quality=85):
    if scale_percentage:
        # Yüzdeyle ölçekleme
        original_width, original_height = image.size
        new_width = int(original_width * scale_percentage / 100)
        new_height = int(original_height * scale_percentage / 100)
    else:
        # En/boy oranına göre ölçekleme
        new_width = width
        new_height = height

    # Görüntüyü yeniden boyutlandır
    resized_img = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Bellekte sıkıştırılmış görüntüyü kaydet
    img_byte_arr = io.BytesIO()
    resized_img.save(img_byte_arr, format="JPEG", quality=quality)
    img_byte_arr.seek(0)
    return img_byte_arr


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Kullanıcıdan dosya yükleme
        file = request.files.get("file")
        mode = request.form.get("mode")  # Kullanıcı tarafından seçilen ölçekleme modu
        quality = int(request.form.get("quality"))
        output_name = request.form.get("output_name")  # Kullanıcıdan alınan dosya adı

        if not file or file.filename == "":
            return "Hata: Lütfen bir JPEG dosyası yükleyin!"

        if not output_name:
            return "Hata: Dosya adı girilmedi!"

        try:
            image = Image.open(file)

            if mode == "scale_percentage":
                scale_percentage = int(request.form.get("scale_percentage"))
                output_image = scale_and_compress(image, scale_percentage=scale_percentage, quality=quality)
            elif mode == "custom_size":
                width = int(request.form.get("width"))
                height = int(request.form.get("height"))
                output_image = scale_and_compress(image, width=width, height=height, quality=quality)
            else:
                return "Hata: Geçersiz ölçekleme modu seçildi!"

            # Kullanıcıya verilen isimle dosyayı döndür
            return send_file(
                output_image,
                as_attachment=True,
                download_name=f"{output_name}.jpg",
                mimetype="image/jpeg"
            )
        except Exception as e:
            return f"Hata: {e}"

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
