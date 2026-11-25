# Extensions Blank pour WordPress

Dépôt de distribution : il ne contient que les zips publiés et `catalog.json`.
Le centre de contrôle de **Blank Core** (menu Extensions de `/tsuki`, réservé au super-admin) lit ce catalogue,
télécharge les zips d'ici et vérifie leur empreinte SHA-256 avant toute installation.

Ne pas modifier à la main : les zips et le catalogue sont produits par `tools/release.py` dans le dépôt source.
Une version publiée n'est jamais remplacée ; toute correction passe par un nouveau numéro de version.
