from string import Template
from datetime import datetime

from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib

def reserv_email(name, number):

    with open('template_reserva.html', 'r', encoding='utf-8') as html:
        template = Template(html.read())
        data_atual = datetime.now().strftime('%d/%m/%Y')
        hora_atual = datetime.now().strftime('%H:%M:%S')
        corpo_msg = template.substitute(nome=name, data=data_atual, hora=hora_atual, numero=number)

    msg = MIMEMultipart()
    msg['from'] = ''
    msg['to'] = ''
    msg['subject'] = 'Atenção: TESTE (Reserva do Hotel)'

    corpo = MIMEText(corpo_msg, 'html')
    msg.attach(corpo)

    with open('image2.jpg', 'rb') as img:
        img = MIMEImage(img.read())
        msg.attach(img)

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login('', '')
        smtp.send_message(msg)
        print('E-mail enviado com sucesso.')

    print(corpo_msg)
