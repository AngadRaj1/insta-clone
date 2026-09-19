import os
import io
import uuid
import boto3
from PIL import Image, ImageOps
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.posts.schemas import PostCreate
from app.domains.posts.repository import PostRepository

class PostService:
    def __init__(self, session: AsyncSession):
        self.repo = PostRepository(session)


    # async def create_post_with_image(self, image: UploadFile, caption: str | None, user_id: uuid.UUID):
    #     # 1. Generate a unique filename using UUID and the original file extension
    #     file_extension = image.filename.split(".")[-1]
    #     unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
    #     # 2. Define the path where the file will be saved locally
    #     file_path = f"uploads/{unique_filename}"
        
    #     # 3. Read the file from the request and write it to our local folder
    #     with open(file_path, "wb") as buffer:
    #         # We use image.file.read() to get the binary data
    #         buffer.write(image.file.read())
            
    #     # 4. Create the URL path that the frontend will use to view the image
    #     image_url = f"/static/{unique_filename}"
        
    #     # 5. Build the PostCreate schema and save it using our existing repository
    #     post_data = PostCreate(image_url=image_url, caption=caption)
    #     return await self.repo.create(post_data, user_id)

    

# Initialize the S3 client using credentials from the environment
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        self.bucket_name = os.getenv("AWS_BUCKET_NAME")

    # async def create_post_with_image(self, image: UploadFile, caption: str | None, user_id: uuid.UUID):
    #     # 1. Generate unique filename
    #     file_extension = image.filename.split(".")[-1]
    #     unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
    #     try:
    #         # 2. Upload directly to AWS S3
    #         self.s3_client.upload_fileobj(
    #             image.file,
    #             self.bucket_name,
    #             unique_filename,
    #             ExtraArgs={"ContentType": image.content_type} # Ensures browsers display it as an image
    #         )
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
            
    #     # 3. Construct the public S3 URL
    #     region = os.getenv("AWS_REGION", "us-east-1")
    #     image_url = f"https://{self.bucket_name}.s3.{region}.amazonaws.com/{unique_filename}"
        
    #     # 4. Save to database
    #     post_data = PostCreate(image_url=image_url, caption=caption)
    #     return await self.repo.create(post_data, user_id)


    def _compress_image(self, file: UploadFile, max_dimension: int = 1080, quality: int = 80) -> io.BytesIO:
        """Resizes the image and compresses it to JPEG format in memory."""
        try:
            image = Image.open(file.file)

            # Auto-orient the image based on EXIF tags (fixes upside-down/sideways phone uploads)
            image = ImageOps.exif_transpose(image)

            # Convert to RGB (handles RGBA PNGs or palette-based images)
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Scale down if width or height exceeds max_dimension
            image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

            # Compress to an in-memory buffer
            output_buffer = io.BytesIO()
            image.save(
                output_buffer,
                format="JPEG",
                quality=quality,
                optimize=True,
            )
            output_buffer.seek(0)
            return output_buffer

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    async def create_post_with_image(self, image: UploadFile, caption: str | None, user_id: uuid.UUID):
        # 1. Compress image in memory
        compressed_buffer = self._compress_image(image, max_dimension=1080, quality=80)
        
        # 2. Always store as .jpeg since we standardized the format
        unique_filename = f"{uuid.uuid4()}.jpeg"

        try:
            # 3. Upload compressed buffer directly to S3
            self.s3_client.upload_fileobj(
                compressed_buffer,
                self.bucket_name,
                unique_filename,
                ExtraArgs={"ContentType": "image/jpeg"},
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

        # 4. Construct S3 public URL
        region = os.getenv("AWS_REGION", "us-east-1")

        if region == "us-east-1":
            image_url = f"https://{self.bucket_name}.s3.amazonaws.com/{unique_filename}"
        else:
            image_url = f"https://{self.bucket_name}.s3.{region}.amazonaws.com/{unique_filename}"

        # 5. Save record to database
        post_data = PostCreate(image_url=image_url, caption=caption)
        return await self.repo.create(post_data, user_id)


    # create new post
    async def create_post(self, post_data: PostCreate, user_id: uuid.UUID):
        # We can add extra business logic here later (like hashtag extraction)
        return await self.repo.create(post_data, user_id)


    async def get_feed(self, limit: int = 20):
        return await self.repo.get_latest(limit)


    async def get_timeline_feed(self, user_id: uuid.UUID, limit: int = 20):
        return await self.repo.get_personalized_feed(user_id, limit)