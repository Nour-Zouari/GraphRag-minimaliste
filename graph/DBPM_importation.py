import requests

url = "https://base-donnees-publique.medicaments.gouv.fr/download/file/CIS_bdpm.txt"
output_path = "data/raw/CIS_bdpm.txt"

resp = requests.get(url)
resp.raise_for_status()
with open(output_path, "wb") as f:
    f.write(resp.content)

print("Fichier BDPM téléchargé et sauvegardé dans", output_path)
