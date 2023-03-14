import asyncio
import aiofiles
import aiosftp

async def upload_images(urls, host, port, username, password):
    async with aiosftp.ClientSession(host, port=port, username=username, password=password) as session:
        for url in urls:
            # Open the image file
            async with aiofiles.open(url, 'rb') as f:
                image_data = await f.read()
            # Get the image filename
            image_name = url.split('/')[-1]
            # Upload the image to the SFTP server
            await session.put(image_data, f'/path/to/upload/{image_name}')
    print("Upload complete")

# Create the urls list
urls = ['url1/picture1.jpg','url2/picture2.jpg']
# run the function
asyncio.run(upload_images(urls, "hostname", "port", "username", "password"))