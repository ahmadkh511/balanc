import os
import magic
from uuid import uuid4
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

class FileUploadSecurity:
    """فئة متخصصة في التحقق الآمن من الملفات المرفوعة"""
    
    ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/webp']
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
    MAX_DIMENSION = 5000  # أقصى عرض أو ارتفاع للصورة

    @classmethod
    def validate_file(cls, uploaded_file):
        """التحقق من الملف المرفوع مع تطبيق جميع الإجراءات الأمنية"""
        cls._check_file_size(uploaded_file)
        cls._check_extension(uploaded_file)
        cls._check_mime_type(uploaded_file)
        cls._check_image_content(uploaded_file)
        cls._sanitize_filename(uploaded_file)

    @classmethod
    def _check_file_size(cls, file):
        if file.size > cls.MAX_FILE_SIZE:
            raise ValidationError(f"حجم الملف يتجاوز الحد المسموح ({cls.MAX_FILE_SIZE/1024/1024}MB)")

    @classmethod
    def _check_extension(cls, file):
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
            raise ValidationError("امتداد الملف غير مسموح")

    @classmethod
    def _check_mime_type(cls, file):
        file.seek(0)
        try:
            mime = magic.from_buffer(file.read(1024), mime=True)
            file.seek(0)
            
            if mime not in cls.ALLOWED_MIME_TYPES:
                raise ValidationError(f"نوع الملف غير مدعوم: {mime}")
        except Exception as e:
            file.seek(0)
            raise ValidationError("تعذر تحديد نوع الملف") from e

    @classmethod
    def _check_image_content(cls, file):
        file.seek(0)
        try:
            with Image.open(file) as img:
                if max(img.size) > cls.MAX_DIMENSION:
                    raise ValidationError(f"أبعاد الصورة تتجاوز الحد الأقصى ({cls.MAX_DIMENSION}px)")
                img.verify()
                
                if img.mode not in ['L', 'RGB', 'RGBA']:
                    raise ValidationError("نوع الصورة اللوني غير مدعوم")
                
            file.seek(0)
        except UnidentifiedImageError:
            raise ValidationError("الملف ليس صورة صالحة")
        except Exception as e:
            raise ValidationError(f"خطأ في محتوى الصورة: {str(e)}")

    @classmethod
    def _sanitize_filename(cls, file):
        """إعادة تسمية الملف باسم آمن باستخدام UUID"""
        ext = os.path.splitext(file.name)[1].lower()
        file.name = f"{uuid4().hex}{ext}"


        # هذا الملف هو من خطوات تحسين الامان 