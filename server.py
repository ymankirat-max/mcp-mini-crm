"""Serveur MCP « mini-CRM ».

Expose un petit CRM (clients + opportunités commerciales, à la manière de
Salesforce) comme des OUTILS qu'un agent IA peut appeler lui-même :
lister, consulter, créer, mettre à jour, repérer les opportunités en retard.

Les données sont stockées dans data/crm.json (fictives).
Lancement : python server.py   (transport stdio, utilisé par Claude Desktop & co)
"""

import json
from datetime import date
from pathlib import Path

from mcp.server import MCPServer

DATA_FILE = Path(__file__).parent / "data" / "crm.json"
STATUTS = ["Prospection", "Qualification", "Proposition", "Négociation", "Gagnée", "Perdue"]

mcp = MCPServer(
    name="mini-crm",
    instructions="CRM de démonstration : clients et opportunités commerciales. "
    "Utilise les outils pour consulter ou mettre à jour le pipeline commercial.",
)


# ---------- Accès aux données ----------

def charger() -> dict:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def sauver(data: dict) -> None:
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def trouver_client(data: dict, client_id: str) -> dict:
    for c in data["clients"]:
        if c["id"] == client_id:
            return c
    raise ValueError(f"Client introuvable : {client_id}")


# ---------- Outils exposés à l'IA ----------
# Chaque fonction décorée par @mcp.tool() devient un outil.
# La docstring sert de description pour l'IA, les annotations de type
# deviennent le schéma JSON des paramètres.

@mcp.tool()
def lister_clients() -> list[dict]:
    """Liste tous les clients du CRM (id, nom, secteur, ville)."""
    return [
        {k: c[k] for k in ("id", "nom", "secteur", "ville")}
        for c in charger()["clients"]
    ]


@mcp.tool()
def fiche_client(client_id: str) -> dict:
    """Fiche complète d'un client avec ses contacts et ses opportunités."""
    data = charger()
    client = trouver_client(data, client_id)
    opps = [o for o in data["opportunites"] if o["client_id"] == client_id]
    return {**client, "opportunites": opps}


@mcp.tool()
def lister_opportunites(statut: str | None = None) -> list[dict]:
    """Liste les opportunités, filtrées par statut si précisé.

    Statuts possibles : Prospection, Qualification, Proposition,
    Négociation, Gagnée, Perdue.
    """
    opps = charger()["opportunites"]
    if statut:
        opps = [o for o in opps if o["statut"].lower() == statut.lower()]
    return opps


@mcp.tool()
def opportunites_en_retard() -> list[dict]:
    """Opportunités encore ouvertes dont la date de clôture prévue est dépassée."""
    aujourd_hui = date.today().isoformat()
    data = charger()
    noms = {c["id"]: c["nom"] for c in data["clients"]}
    return [
        {**o, "client": noms.get(o["client_id"])}
        for o in data["opportunites"]
        if o["statut"] not in ("Gagnée", "Perdue") and o["date_cloture"] < aujourd_hui
    ]


@mcp.tool()
def creer_opportunite(client_id: str, titre: str, montant: float, date_cloture: str) -> dict:
    """Crée une opportunité (statut Prospection) pour un client existant.

    date_cloture au format AAAA-MM-JJ.
    """
    date.fromisoformat(date_cloture)  # lève une erreur si le format est faux
    data = charger()
    trouver_client(data, client_id)
    nouvelle = {
        "id": f"OPP-{len(data['opportunites']) + 1:03d}",
        "client_id": client_id,
        "titre": titre,
        "montant": montant,
        "statut": "Prospection",
        "date_cloture": date_cloture,
    }
    data["opportunites"].append(nouvelle)
    sauver(data)
    return nouvelle


@mcp.tool()
def changer_statut(opportunite_id: str, statut: str) -> dict:
    """Change le statut d'une opportunité (ex. passer en Négociation ou Gagnée)."""
    if statut not in STATUTS:
        raise ValueError(f"Statut invalide. Choix : {', '.join(STATUTS)}")
    data = charger()
    for o in data["opportunites"]:
        if o["id"] == opportunite_id:
            o["statut"] = statut
            sauver(data)
            return o
    raise ValueError(f"Opportunité introuvable : {opportunite_id}")


if __name__ == "__main__":
    mcp.run()  # stdio par défaut
