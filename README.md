Este script toma el export de checklists generados de powerBI y lo cruza con constantes de grupos de resolucion, coordinadores, regiones, torre, etc. para generar un archivo utilizado para la carga masiva de tickets de PDM.


Por cada checklist generado, se genera una entrada para solicitud masiva de ticket.

Actualmente valida si la Region y la Torre esta bien escrita en el input (esto para eviar generar tkts con titulos erroneos)
Si se detecta un error en este punto, de darse aviso al generador el input
