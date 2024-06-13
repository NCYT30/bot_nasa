from config import TELEGRAM_TOKEN
import telebot
import requests
import random
from datetime import datetime, timedelta
from random import choice

API_KEY = 'tu_api' 
bot = telebot.TeleBot(TELEGRAM_TOKEN)

markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
markup.add('Imagenes astronomicas', 'Tierra', 'asteroides cercanos', 'Imagenes del robot Rover Marte')

@bot.message_handler(commands=["start"])
def cmd_start(message):
    command_list = "\n".join([
        '/start - Inicia la conversacion',
        'Imagenes astronomicas',
        'Tierra',
        'asteroides cercanos', 
        'Imagenes del robot Rover Marte'
    ])
    bot.send_message(message.chat.id, f'Hola! ¿Qué deseas hacer?\n\nAquí tienes una lista de comandos disponibles:\n{command_list}', reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if 'imagenes astronomicas' in message.text.lower():
        buscar_astronomia(message)
    elif 'tierra' in message.text.lower():
        buscar_tierra(message)
    elif 'asteroides cercanos' in message.text.lower():
        asteroides_cercanos('2024-06-10', '2024-06-11', message)
    elif 'Imagenes del robot Rover Marte':
        marte(message, bot)
    else:
        bot.reply_to(message, 'No entendí tu respuesta. Por favor, elige una opción válida.', reply_markup=markup)

def buscar_astronomia(message):
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

    url = 'https://api.nasa.gov/planetary/apod'
    params = {
        'api_key': API_KEY,
        'date': random_date.strftime('%Y-%m-%d')
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'url' in data:
            image_url = data['url']
            explanation = data.get('explanation', 'No hay explicación disponible.')
            if len(explanation) > 500:
                explanation_short = explanation[:500] + '...'
            else:
                explanation_short = explanation
            caption = f"Explicación: {explanation_short}\n\nMás detalles: [NASA](https://apod.nasa.gov/apod/astropix.html)"
            bot.send_photo(message.chat.id, image_url, caption=caption, parse_mode='HTML')
        else:
            bot.reply_to(message, "No se encontraron resultados para la búsqueda.")
    except requests.exceptions.RequestException as err:
        bot.reply_to(message, "Ocurrió un error al buscar la imagen astronómica.")
        print(err)

    bot.send_message(message.chat.id, '¿Qué deseas hacer ahora?', reply_markup=markup)

def buscar_tierra(message):
    max_attempts = 10 
    attempt = 0
    found_image = False

    while attempt < max_attempts and not found_image:
        try:
            start_date = datetime.now() - timedelta(days=5*365)
            end_date = datetime.now()
            random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

            url = 'https://api.nasa.gov/planetary/earth/assets'
            params = {
                'lon': 100.75,      
                'lat': 1.5,      
                'dim': 0.1,         
                'date': random_date.strftime('%Y-%m-%d'),
                'api_key': API_KEY
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if "url" in data:
                image_url = data["url"]
                date = random_date.strftime('%Y-%m-%d')
                caption = f"Fecha de la imagen: {date}\n\nImagen de la Tierra"
                bot.send_photo(message.chat.id, image_url, caption=caption, parse_mode='HTML')
                found_image = True
            else:
                attempt += 1
                print(f"Intento {attempt} fallido: No se encontró URL de imagen en la respuesta.")

        except requests.exceptions.RequestException as err:
            attempt += 1
            print(f"Intento {attempt} fallido: {err}")

    if not found_image:
        bot.reply_to(message, "No se encontraron imágenes disponibles después de varios intentos.")
    else:
        bot.send_message(message.chat.id, '¿Qué deseas hacer ahora?', reply_markup=markup)




def asteroides_cercanos(start_date, end_date, message):
    url = f'https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&'
    params = {
        'api_key': API_KEY 
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    near_earth_objects = data.get('near_earth_objects', {})
    if near_earth_objects:
        random_day = random.choice(list(near_earth_objects.keys()))
        asteroids_info = near_earth_objects.get(random_day, [])
        if asteroids_info:
            random_asteroid = random.choice(asteroids_info)
            name = random_asteroid.get('name', 'No disponible')
            absolute_magnitude_h = random_asteroid.get('absolute_magnitude_h', 'No disponible')
            estimated_diameter_min = random_asteroid.get('estimated_diameter', {}).get('kilometers', {}).get('estimated_diameter_min', 'No disponible')
            is_potentially_hazardous = random_asteroid.get('is_potentially_hazardous_asteroid', 'No disponible')
            close_approach_date = random_asteroid.get('close_approach_data', [{}])[0].get('close_approach_date', 'No disponible')
            bot.send_message(message.chat.id, f"Nombre: {name}\nMagnitud Absoluta: {absolute_magnitude_h}\nDiámetro Estimado Mínimo: {estimated_diameter_min}\nPotencialmente Peligroso: {is_potentially_hazardous}\nFecha de Acercamiento: {close_approach_date}")
        else:
            bot.reply_to(message, 'No se encontraron asteroides para el día especificado')
    else:
        bot.reply_to(message, 'No se encontraron asteroides en la respuesta')


def marte(message, bot):
    url = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos'
    params = {
        'sol': 1000,
        'api_key': 'DEMO_KEY'
    }
    response = requests.get(url, params=params)
    data = response.json()

    if 'photos' in data and len(data['photos']) > 0:
        photos = [photo['img_src'] for photo in data['photos']]
        random_photo = choice(photos)
        bot.send_photo(chat_id=message.chat.id, photo=random_photo, caption="Aquí tienes una imagen de Marte 🚀")
    else:
        bot.reply_to(message, 'Lo siento, no se encontraron imágenes de Marte en este momento.')

if __name__ == '__main__':
    print('Bot iniciado')
    bot.infinity_polling()
    print('Fin')
