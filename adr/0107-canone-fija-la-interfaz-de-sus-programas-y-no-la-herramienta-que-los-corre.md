# ADR-0107 · canone fija la interfaz de sus programas, y no la herramienta que los corre

- **Estado:** Aceptada
- **Fecha:** 2026-10-29
- **Alcance:** «Responsabilidades» de [`README.md`](../README.md), las carpetas del raíz de
  [`repositorio.md`](../repositorio.md) y `plantilla/.gitignore`

## Contexto

consola es una herramienta independiente que, entre otras cosas, corre los programas de canone.
Varias reglas de canone fijaban cómo trabaja: el
[ADR-0075](0075-canone-fija-el-repositorio-declara-y-consola-dispara.md) le daba una fila en
«Quién hace qué» y le pedía agregar a canone lo que no tuviera plantilla; el
[ADR-0076](0076-lo-que-cambia-entre-despliegues-sale-de-un-solo-archivo-y-lo-demas-es-codigo.md)
ponía lo que cambia entre despliegues en `.consola/config.env`, como única fuente, y le dejaba
resolver un gestor de contraseñas; el
[ADR-0105](0105-las-credenciales-las-cifra-credentials-py-de-canone-y-consola-solo-se-las-pasa.md)
decía de dónde saca lo que le pasa a `credentials.py`, y el
[ADR-0084](0084-ssh-solo-acepta-llaves-y-root-no-entra.md), cuándo pide la contraseña de `sudo`.
`repositorio.md` describía `.consola/`, y la plantilla del `.gitignore` la ignoraba.

Los programas ya se corren sin consola: `infra.yml` instala, despliega y respalda con `ssh` y sus
argumentos, dentro de `systemd-nspawn`.

## Decisión

1. canone fija cada programa por su interfaz: los argumentos de `install.py`, `deploy.py`,
   `backup.sh` y `backup.ps1`, y el stdin de `credentials.py`, que documenta `despliegue.md`. No
   nombra la herramienta que los corre ni fija cómo guarda sus datos. Reemplaza el punto 3 del
   ADR-0075.
2. Lo que cambia entre despliegues, secreto o no, no se commitea: el repositorio declara el campo, y
   el valor llega al servidor como argumento de `install.py` o por `credentials.py`. canone no fija
   dónde lo guarda quien despliega. Reemplaza el punto 4 del ADR-0075, los puntos 2 y 4 del
   ADR-0076 y el punto 2 del ADR-0105.
3. Lo que instalan los programas de canone en una máquina no lo escribe nadie más: ni
   unidades, ni configuración, ni scripts propios.
4. `sudo` pide la contraseña de la cuenta. Reemplaza el punto 4 del ADR-0084, que además decía
   cuándo la pide consola.
5. El repositorio declara su nombre, sus superficies y los campos de `Settings`. El dominio y la
   memoria cambian entre despliegues y son argumentos de `install.py`.
6. `repositorio.md` no describe la carpeta de una herramienta, y `plantilla/.gitignore` no la
   ignora.

## Consecuencias

- canone no menciona a consola en sus reglas vigentes. Los ADR viejos la siguen nombrando en su
  contexto y sus consecuencias, que son historia.
- Una herramienta que guarda datos dentro del repositorio los ignora ella misma, por ejemplo con
  un `.gitignore` dentro de su carpeta. Un repositorio armado desde la plantilla ya no ignora
  `.consola/`.
- Que lo que no tiene plantilla se agregue primero a canone pasa a ser una regla de consola, si la
  quiere. Del lado de canone ya lo dice el `README.md`: lo que una convención exige en una máquina,
  canone lo da como el programa que la deja así.
- Dónde se guarda una copia de lo que cambia entre despliegues fuera de la máquina de quien
  despliega deja de ser una pregunta de canone, salvo `restic_password`
  ([ADR-0074](0074-las-credenciales-del-respaldo-tienen-una-copia-fuera-del-servidor.md)).

## Descartado

- **Dejar `.consola/config.env` como única fuente:** ata la norma a una herramienta, y quien
  despliega a mano o con otra no tiene cómo cumplirla.
- **Fijar el formato de los datos de quien despliega:** canone ya recibe los valores por la
  interfaz de cada programa; cómo los junta una herramienta antes no cambia la máquina.
