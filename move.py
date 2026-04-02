from onvif import ONVIFCamera
import time

# Suas credenciais
IP = "192.168.0.7"
USER = "camera_sala"
PASS = "abc852456"
PORT = 2020

def move_camera():
    mycam = ONVIFCamera(IP, PORT, USER, PASS)

    # 1. Criar o serviço PTZ
    ptz = mycam.create_ptz_service()

    # 2. Obter o perfil de mídia (necessário para saber onde aplicar o movimento)
    media = mycam.create_media_service()
    profile = media.GetProfiles()[0]
    token = profile.token

    # 3. Criar a requisição de movimento
    request = ptz.create_type('ContinuousMove')
    request.ProfileToken = token

    # Definir velocidade: x (pan), y (tilt), z (zoom)
    # Valores variam de -1.0 a 1.0
    request.Velocity = {'PanTilt': {'x': 0.5, 'y': 0}, 'Zoom': {'x': 0}}

    print("Movendo para a direita...")
    ptz.ContinuousMove(request)
    
    # Manter o movimento por 1 segundo
    time.sleep(1)

    # 4. PARAR o movimento (obrigatório, senão ela bate no limite e força o motor)
    ptz.Stop({'ProfileToken': token})
    print("Parou.")

if __name__ == "__main__":
    move_camera()