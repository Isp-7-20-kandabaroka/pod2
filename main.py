from aiogram import Bot, Dispatcher, executor, types
import os
from pytube import YouTube
import instaloader
import vk_api
import requests

# Установка пути для загрузки файлов
download_path = "vid"

# Инициализация объекта Instaloader
insta_loader = instaloader.Instaloader()

# Установка токена Telegram бота
API_TOKEN = '6774261251:AAHkILsM47VYQFPCAJyUDkPt1Hdkew_bCMY'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Создание папки для загрузки файлов, если ее нет
if not os.path.exists(download_path):
    os.makedirs(download_path)

vk_session = vk_api.VkApi(token='dbb0e388dbb0e388dbb0e38839d8a7a3eeddbb0dbb0e388be7bd36b178a01f0575884de')


def download_vk_video(url, vk_session):
    try:
        vk = vk_session.get_api()
        video_id = url.split('/')[-1].split('_')
        owner_id, video_id = video_id[0], video_id[1]
        response = vk.video.get(owner_id=owner_id, videos=f"{owner_id}_{video_id}", count=1)

        if response['items']:
            video_url = response['items'][0]['player']
            video_data = requests.get(video_url)
            filename = f"{download_path}/vk_{owner_id}_{video_id}.mp4"
            with open(filename, 'wb') as f:
                f.write(video_data.content)
            return filename
    except Exception as e:
        print(f"Error downloading VK video: {e}")
        return None


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(
        'Привет! Просто отправь мне ссылку на видео с Instagram, YouTube или ВКонтакте, и я попытаюсь его скачать и отправить тебе.')


def download_instagram_video(url):
    try:
        post = instaloader.Post.from_shortcode(insta_loader.context, url.split('/')[-1])
        filename = f"{download_path}/{post.owner_username}_{post.shortcode}.mp4"
        insta_loader.download_post(post, target=filename)
        return filename
    except Exception as e:
        print(f"Error downloading Instagram video: {e}")
        return None


def download_youtube_video(url):
    try:
        yt = YouTube(url)
        video = yt.streams.filter(progressive=True, file_extension='mp4').first()
        filename = video.default_filename
        video.download(output_path=download_path)
        return os.path.join(download_path, filename)
    except Exception as e:
        print(f"Error downloading YouTube video: {e}")
        return None


@dp.message_handler()
async def download_and_send_video(message: types.Message):
    url = message.text
    filename = None
    if 'instagram.com' in url:
        filename = download_instagram_video(url)
    elif 'youtube.com' in url or 'youtu.be' in url:
        filename = download_youtube_video(url)
    elif 'vk.com' in url:
        filename = download_vk_video(url, vk_session)
    else:
        await message.reply('Пожалуйста, отправьте мне ссылку на видео из Instagram, YouTube или ВКонтакте.')
        return

    if filename:
        await message.reply('Видео скачано, отправляю...')
        with open(filename, 'rb') as video_file:
            await bot.send_video(message.chat.id, video_file)
        os.remove(filename)
    else:
        await message.reply('Не удалось скачать видео.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)