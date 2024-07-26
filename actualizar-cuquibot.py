import subprocess
def conseguir_imagenes():
    imagenes_texto= subprocess.check_output(['sudo docker images --format "{{ .Tag }}" cuquibot'], text=True, shell=True)
    imagenes_lista = [x.replace('"', '').strip() for x in imagenes_texto.split("\n")]
    print(f"Obtenidas las siguientes imágens: {imagenes_lista}")
    return imagenes_lista

def seleccionar_masalta(lista):
    lista_listas = [x.strip().split(".") for x in lista if x.strip() != "latest" and x.strip() != '']
    lista_ints = [[int(x) for x in version] for version in lista_listas]
    cero = 0
    uno = 0
    dos = 0
    for version in lista_ints:
        if version[0] > cero:
            cero = version[0]
            uno = 0
            dos = 0
        if version[1] > uno and version[0] >= cero:
            uno = version[1]
            dos = 0
        if version[2] > dos and version[1] >= uno and version[0] >= cero:
            dos = version[2]
    masalta = [cero, uno, dos]
    print(f"La imagen más alta encontrada fue {masalta}")
    return masalta

def aumentar_version(version_vieja: list[int]):
    version_nueva = version_vieja.copy()
    version_nueva[-1] += 1
    print(f"Versión cambiada de {version_vieja} a {version_nueva}")
    return version_nueva

def procesar_imagenes(v: list[int]):
    subprocess.run(f'sudo docker build --tag cuquibot:{v[0]}.{v[1]}.{v[2]} .', text=True, shell=True)
    subprocess.run(f'sudo docker rmi cuquibot:latest', text=True, shell=True)
    subprocess.run(f'sudo docker tag cuquibot:{v[0]}.{v[1]}.{v[2]} cuquibot:latest', text=True, shell=True)
    print("Creada y tageada la nueva imagen.")

def main():
    subprocess.run('sudo docker-compose down', text=True, shell=True)
    print("Bajado el contenedor")

    imagenes = conseguir_imagenes()
    version = seleccionar_masalta(imagenes)
    nueva_version = aumentar_version(version)
    procesar_imagenes(nueva_version)

    print("Subiéndola a un contenedor...")
    subprocess.run('sudo docker-compose up -d', text=True, shell=True)
    print("Subido el contenedor! <3")
    status = subprocess.run('sudo docker ps -f name=cuquibot', text=True, shell=True)
    print(status.stdout)
    print("Actualización de versión finalizada :)")

if __name__ == "__main__":
    main()
