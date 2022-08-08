# Instrucciones de Instalación

### Actualizar e instalar paquetes necesarios
sudo apt update<br>
sudo apt upgrade<br>
sudo apt install git curl libffi-dev libssl-dev python3-dev python3 python3-pip virtualenv build-essential python3-smbus<br>

### Clonación del repositorio
git clone https://github.com/EB1TR/py-rotor-ctrl.git

### Preparamos entornos virtuales en el Host
cd /home/pi<br>
mkdir venvs<br>
mkdir venvs/feedback<br>
mkdir venvs/mando<br>
virtualenv venvs/feedback<br>
virtualenv venvs/mando<br>

### Instalación de paquetes para el Feedback de dirección
source venvs/feedback/bin/activate<br>
pip install --upgrade pip<br>
pip install paho-mqtt adafruit_ads1x15<br>
deactivate<br>

### Instalación de paquetes para el Control de dirección
source venvs/mando/bin/activate<br>
pip install --upgrade pip<br>
pip install paho-mqtt<br>
deactivate<br>

### Modificamos rc.local para lanzar tareas en el Host
sudo cp py-rotor-ctrl/resources/rc.local /etc/rc.local<br>

### Reboot
sudo shutdown -r now<br>
