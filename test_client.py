"""Client de test : lance le serveur, liste ses outils et en appelle quelques-uns.

Usage : python test_client.py
(Ne modifie pas data/crm.json : n'appelle que des outils en lecture.)
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = Path(__file__).parent / "server.py"


async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Outils exposés :")
            for t in tools.tools:
                print(f"  - {t.name} : {t.description.splitlines()[0]}")

            for name, args in [
                ("lister_clients", {}),
                ("opportunites_en_retard", {}),
                ("fiche_client", {"client_id": "CLI-002"}),
            ]:
                res = await session.call_tool(name, args)
                print(f"\n>>> {name}({args})")
                for block in res.content:
                    print(getattr(block, "text", block))


if __name__ == "__main__":
    asyncio.run(main())
