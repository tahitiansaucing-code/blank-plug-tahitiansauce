# Extensions Blank pour WordPress

Dépôt de distribution public : il contient les zips publiés et `catalog.json`.
Sur chaque site, **Blank Core** lit ce catalogue dans **wp-admin → Extensions → Extensions Blank**
(page réservée au super-admin). On y voit la liste, et on peut installer, mettre à jour, activer,
désactiver, supprimer ou télécharger chaque extension. Chaque zip est vérifié (empreinte SHA-256)
avant d'être installé.

## Ajouter ou mettre à jour une extension

1. Prépare le zip de l'extension :
   - un seul dossier à l'intérieur, nommé `blank-quelquechose` (minuscules, chiffres, tirets) ;
   - dans ce dossier, le fichier principal `blank-quelquechose.php` avec cet en-tête :

     ```php
     <?php
     /**
      * Plugin Name:      Blank Quelque chose
      * Description:      Une phrase qui dit ce que fait l'extension.
      * Version:          1.0.0
      * Requires Plugins: blank-core, woocommerce
      */
     ```

     `Requires Plugins` est facultatif (seulement `blank-…` ou `woocommerce`).
2. Sur GitHub, ouvre le dossier **zips**, puis **Add file → Upload files**, dépose le zip
   (le nom du fichier n'a pas d'importance) et clique **Commit changes**.
3. L'onglet **Actions** lance « Catalogue » tout seul (environ 30 secondes) :
   - il nettoie les fichiers cachés Mac/Windows, renomme le zip en `blank-quelquechose-1.0.0.zip`
     et met `catalog.json` à jour ;
   - pastille verte : c'est publié. Sur les sites, la nouvelle version apparaît dans les 5 minutes
     (bouton « Vérifier le catalogue ») ;
   - pastille rouge : ouvre le détail, la ligne « REFUSÉ : … » dit pourquoi. Supprime le zip refusé,
     corrige-le et dépose-le à nouveau. Le catalogue n'a pas changé.

## Règles

- Pour une mise à jour, augmente toujours la version (1.0.0 → 1.0.1). Une version publiée n'est jamais
  remplacée : déposer la même version avec un autre contenu est refusé.
- Les sites ne reviennent jamais à une version plus ancienne que celle installée.
- Ne mets jamais de clé, de mot de passe ni de jeton dans une extension : ce dépôt est public.
  Les secrets se saisissent dans les réglages de chaque site.
- Ne modifie pas `catalog.json` à la main : il est reconstruit à chaque dépôt de zip.
