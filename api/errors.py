# coding=utf-8
# Api error code : XYYZZ
# X API version
# YY Model attached
# ZZ error number

error_codes = {
    # global
    "10900": "Désolé, la requête que vous avez effectuée semble incorrecte.",
    "10666": "Une erreur inconnue est survenue",
    "10215": "La date de debut de votre annonce doit etre anterieure a la date de fin",
    "10216": "Vous n'avez pas le droit de modifier cette annonce",
    "10217": "Vous ne pouvez accepter votre propre annonce",
    "10218": "La quantité que vous avez saisie est incorrecte. Elle est sois negative sois supérieure à la quantité disponible",
    "10219": "La date de début de votre annonce ne peut être antérieure à la date du jour",
    "10220": "Vous ne pouvez pas accepter cette annonce",
    "10221": "Aucune image n'a été détectée",
    "10222": "Vous n'avez pas le droit de supprimer cette image",
    "10223": "Vous n'avez pas le droit d'effectuer cette action"
}


class BadParameterError(Exception):
    """
    Bad parameter exception
    """

    def __init__(self, parameter):
        self.code = 10410
        self.message = error_codes['10410'] % parameter