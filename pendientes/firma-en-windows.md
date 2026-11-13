# La firma de los instaladores de Windows

Tema pendiente: **sin decidir**. Hay que decidirlo antes de la primera versión pública de una app de `desktop/`.

## Estado (verificado 2026-11-13)

El `setup.exe` de Flet y el `.exe` de Qt salen sin firmar. Microsoft Defender SmartScreen muestra «Windows protected your PC», con *Unknown publisher*, y el usuario tiene que elegir «More info» y «Run anyway». Con Smart App Control activo, Windows 11 puede bloquear la app ([*Code signing*](../fuentes/flet/publish-windows.md) de Flet).

## Opciones

| Opción | Qué da | Costo |
| :--- | :--- | :--- |
| Sin firma | Nada: el aviso queda siempre | Ninguno |
| Certificado de una autoridad certificadora | El nombre del editor en lugar de *Unknown publisher*. El aviso sigue hasta que el archivo o el certificado ganan reputación con las descargas | Un certificado por año y su llave en el CI |
| Servicio de firma de Microsoft en Azure | Lo mismo, con la llave en Azure y la firma desde el CI | **Sin confirmar**: el precio y quién puede usarlo |
| Microsoft Store | Microsoft firma la app | La cuenta de la tienda y el paquete MSIX |

## Recomendación

El servicio de firma de Microsoft, si la cuenta puede usarlo: la llave no sale de Azure y no hay un certificado que renovar a mano. Si no puede, un certificado de una autoridad certificadora. Antes de decidir hay que comprobar el precio y los requisitos del servicio.
