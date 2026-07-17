import httpx
from app.core.config import settings

def delete_image_from_supabase(image_url: str):
    """
    Menghapus gambar dari bucket Supabase Storage jika URL valid.
    Fungsi ini bersifat synchronous agar mudah dipanggil dari service.
    """
    if not image_url or not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return

    # Pastikan URL tersebut milik Supabase project kita
    if settings.SUPABASE_URL not in image_url:
        return

    try:
        # Ekstrak filename dari URL, e.g. "uuid.jpg"
        # URL format: https://[URL]/storage/v1/object/public/products/uuid.jpg
        filename = image_url.split("/")[-1]
        bucket_name = "products"
        
        # Endpoint DELETE: /storage/v1/object/{bucket}/{filename}
        delete_url = f"{settings.SUPABASE_URL}/storage/v1/object/{bucket_name}/{filename}"
        
        headers = {
            "Authorization": f"Bearer {settings.SUPABASE_KEY}",
            "apikey": settings.SUPABASE_KEY,
        }
        
        with httpx.Client() as client:
            response = client.delete(delete_url, headers=headers)
            if response.status_code not in (200, 204):
                print(f"Failed to delete image {filename} from Supabase: {response.text}")
    except Exception as e:
        print(f"Error deleting image from Supabase: {str(e)}")
