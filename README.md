C’est un petit programme en Python qui sert à surveiller automatiquement des API (ou des sites web).
Il fait trois choses principales :

Vérifie régulièrement si l’API ou le site fonctionne correctement (réponse OK, code 200).

Mesure le temps de réponse pour voir si c’est rapide ou lent.

Alerte par e‑mail si un service ne répond pas ou renvoie une erreur plusieurs fois de suite.

Il affiche aussi un petit tableau de bord dans un navigateur (via une page web simple avec Flask) où tu peux voir :

Le nom de chaque API surveillée

L’URL

Le dernier code de réponse reçu

Le temps de réponse en secondes

La date et l’heure du dernier test

La liste des API à surveiller et la configuration email sont mises dans un petit fichier config.json, facile à modifier.

En résumé :
📡 Il prévient si une API tombe en panne et te donne un aperçu simple de leur état depuis ton navigateur.

Si tu veux, je peux aussi te faire un schéma visuel qui explique comment tout ça fonctionne.
Veux-tu que je te fasse ce schéma ?
