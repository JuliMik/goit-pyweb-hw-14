import cloudinary
import cloudinary.uploader
import cloudinary.api

# Налаштування Cloudinary
cloudinary.config(
  cloud_name="your_name",
  api_key="your_key",
  api_secret="your_api_secret",
  secure=True
)
