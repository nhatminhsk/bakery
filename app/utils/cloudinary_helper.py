import cloudinary
import cloudinary.uploader


def init_cloudinary(app):
    cloudinary.config(
        cloud_name = app.config.get('CLOUDINARY_CLOUD_NAME'),
        api_key    = app.config.get('CLOUDINARY_API_KEY'),
        api_secret = app.config.get('CLOUDINARY_API_SECRET'),
    )


def upload_image(file, folder='bakery'):
    result = cloudinary.uploader.upload(
        file,
        folder=folder,
        transformation=[
            {'width': 800, 'crop': 'limit'},
            {'quality': 'auto'},
            {'fetch_format': 'auto'},
        ]
    )
    return result['secure_url'], result['public_id']


def delete_image(public_id):
    try:
        cloudinary.uploader.destroy(public_id)
    except Exception:
        pass
