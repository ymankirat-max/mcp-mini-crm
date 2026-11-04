# mini-CRM — serveur MCP

Serveur [MCP (Model Context Protocol)](https://modelcontextprotocol.io) en Python qui expose un petit CRM
(clients + opportunités commerciales, sur le modèle de Salesforce) comme des **outils** qu'un agent IA
peut appeler lui-même.

Exemple de demande à l'IA : *« Quelles opportunités sont en retard ? Passe celle de TransLog en Négociation. »*
→ l'IA appelle `opportunites_en_retard`, puis `changer_statut`.

## Outils exposés

| Outil | Rôle |
|---|---|
| `lister_clients` | Liste les clients |
| `fiche_client` | Fiche d'un client + contacts + opportunités |
| `lister_opportunites` | Liste les opportunités (filtre par statut) |
| `opportunites_en_retard` | Opportunités ouvertes dont la date de clôture est dépassée |
| `creer_opportunite` | Crée une opportunité pour un client |
| `changer_statut` | Fait avancer une opportunité dans le pipeline |

## Installation

```bash
pip install -r requirements.txt
python test_client.py      # lance le serveur, liste les outils, appelle les outils de lecture
```

## Brancher sur Claude Desktop

Dans `%APPDATA%\Claude\claude_desktop_config.json` :

```json
{
  "mcpServers": {
    "mini-crm": {
      "command": "python",
      "args": ["C:\\chemin\\vers\\mcp-mini-crm\\server.py"]
    }
  }
}
```

Redémarrer Claude Desktop : les 6 outils apparaissent.

## Comment ça marche

1. `MCPServer("mini-crm")` crée le serveur.
2. Chaque fonction décorée par `@mcp.tool()` devient un outil :
   - la **docstring** = description lue par l'IA pour savoir quand l'utiliser ;
   - les **annotations de type** (`client_id: str`, `montant: float`) = schéma JSON des paramètres.
3. `mcp.run()` démarre le serveur en **stdio** : le client IA (Claude Desktop…) lance le processus et
   échange avec lui des messages JSON-RPC.
4. Les données sont dans `data/crm.json` (fictives). En production, on remplacerait `charger()` / `sauver()`
   par des appels à l'API REST de Salesforce — le reste du serveur ne change pas.

## Pistes d'amélioration

- Brancher l'API REST Salesforce (sandbox) à la place du JSON.
- Ajouter un outil « rédiger un mail de relance » pour les opportunités en retard.
- Authentification et droits (lecture seule vs écriture).
